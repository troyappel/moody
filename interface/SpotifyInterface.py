import time
from typing import Tuple, Callable
from enum import Enum
import gym

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import numpy as np

import configparser

import ray

from interface.GenericInterface import GenericInterface

from models.SpotifyModel import SpotifyModel

class SpotifyInterface(GenericInterface):

    scope = "user-read-currently-playing user-read-playback-state streaming"

    def __init__(self, config, callback_interval, **kwargs):
        self.config = config
        self.callback_interval = callback_interval
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope=self.scope,
            client_id=config['SPOTIFY']['CLIENT_ID'],
            client_secret=config['SPOTIFY']['CLIENT_SECRET'],
            redirect_uri=config['SPOTIFY']['REDIRECT_URI'],
            username=config['SPOTIFY']['USERNAME']
        ))

        print()

        self.uri_set = set()

        self.cum_reward = 0

        self.SET_SIZE = 200

        print('config ids!')
        self.config_ids()

        GenericInterface.__init__(self, config, callback_interval, SpotifyModel(**kwargs))

    # Calls to super should be here!
    def init_in_task(self, self_actor) -> None:
        print("spotify ready!")
        self.ready()

    def get_interval_data(self) -> dict:
        cur = self.sp.current_playback()

        while cur is None:
            time.sleep(3)
            try:
                self.sp.start_playback()
                cur = self.sp.current_playback()
            except spotipy.SpotifyException:
                continue

        volume = cur['device']['volume_percent']

        trackinfo = self.sp.audio_features(cur['item']['id'])[0]

        attrs = np.array([
            float(trackinfo['acousticness']),
            float(trackinfo['danceability']),
            float(trackinfo['energy']),
            float(trackinfo['instrumentalness']),
            float(trackinfo['liveness']),
            float(trackinfo['loudness']),
            float(trackinfo['speechiness']),
            float(trackinfo['valence']),
            float(trackinfo['tempo']),
            volume,
            trackinfo['mode']
        ])

        return {
            'attributes': attrs,
        }


    def action_callback(self, action) -> None:

        cur = self.sp.currently_playing()

        play_now = False

        # Pause means bad song
        if not cur or not cur['is_playing']:
            self.cum_reward -= 100
            play_now = True
        elif not self.new_song_needed():
            return

        attrs = action['attributes']

        self.play_similar(list(attrs), play_now)

    def reward(self):
        return self.cum_reward

    def clear_reward(self):
        self.cum_reward = 0

    # Custom functions
    def config_ids(self):
        artists = self.config['SeedArtists'].keys()
        tracks = self.config['SeedTracks'].keys()

        for artist in artists:
            if self.config['SeedArtists'][artist]:
                continue
            results = self.sp.search(q='artist:' + artist, type='artist')
            self.config['SeedArtists'][artist] = results['artists']['items'][0]['id']

        for track in tracks:
            if self.config['SeedTracks'][track]:
                continue
            results = self.sp.search(q='track:' + track, type='track')
            self.config['SeedTracks'][track] = results['tracks']['items'][0]['id']

        with open('config.txt', 'w') as configfile:
            self.config.write(configfile)

    def seek_song(self, uri, timeout=10):
        prev_uri = None

        # Need to time out if we see playing song is not changing -- happens if there are duplicate things
        try_count = 0

        for _ in range(0, timeout):
            cur_uri = self.sp.currently_playing()['item']['uri']
            print(prev_uri, cur_uri, uri)
            if cur_uri == uri:
                break
            elif cur_uri == prev_uri:
                if try_count > 5:
                    self.sp.next_track()
                    try_count = 0
                try_count += 1
                time.sleep(1)
                continue
            else:
                try_count = 0
                prev_uri = cur_uri
                time.sleep(3)
                self.sp.next_track()

    def play_song(self, uri, now=True):
        while not self.sp.currently_playing()['is_playing']:
            try:
                self.sp.start_playback()
            except spotipy.SpotifyException:
                continue

        self.sp.add_to_queue(uri)

        if now:
            self.seek_song(uri)

    def play_similar(self, target_attrs, now=True):
        print('adding song to queue')
        recs = self.sp.recommendations(
            seed_artists=self.config['SeedArtists'].values(),
            seed_genres=self.config['SeedGenres'].keys(),
            seed_tracks=self.config['SeedTracks'].values(),
            target_acousticness=target_attrs[0],
            target_danceability=target_attrs[1],
            target_energy=target_attrs[2],
            target_liveness=target_attrs[3],
            target_loudness=target_attrs[4],
            target_speechiness=target_attrs[5],
            target_valence=target_attrs[6],
            target_tempo=target_attrs[7],
            target_mode=round(target_attrs[10])
        )

        for track in recs['tracks']:
            if track['uri'] in self.uri_set:
                continue
            else:
                self.play_song(track['uri'], now=now)
                self.uri_set.add(track['uri'])
                if len(self.uri_set) > self.SET_SIZE:
                    self.uri_set.pop()
                break
        else:
            raise Exception()

    def new_song_needed(self):
        playback = self.sp.current_playback()

        to_end = playback['item']['duration_ms'] - playback['progress_ms']

        return to_end < self.callback_interval * 1000
