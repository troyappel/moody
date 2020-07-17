import time
from typing import Tuple, Callable
from enum import Enum
import gym

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import numpy as np

import configparser

from . import GenericInterface

class SpotifyInterface(GenericInterface):

    scope = "user-read-currently-playing user-read-playback-state streaming"

    def __init__(self, config, callback_interval):
        self.config = config
        self.callback_interval = callback_interval
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope=self.scope,
            client_id=config['SPOTIFY']['CLIENT_ID'],
            client_secret=config['SPOTIFY']['CLIENT_SECRET'],
            redirect_uri=config['SPOTIFY']['REDIRECT_URI'],
            username=config['SPOTIFY']['USERNAME']
        ))

        self.uri_set = set()

        self.config_ids()


    def input_space(self) -> gym.spaces.space:
        return self.get_space()

    def output_space(self) -> gym.spaces.space:
        return self.get_space()

    def get_observation(self) -> Tuple:
        cur = self.sp.current_playback()

        volume = cur['device']['volume_percent']

        trackinfo = self.sp.track(cur['item']['id'])

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
            volume
        ])

        mode = np.array([trackinfo['mode']])

        return (attrs, mode)


    def action_callback(self, action) -> Callable:
        if not self.new_song_needed():
            return

        attrs, mode = action

        self.play_similar(list(attrs), mode.item(0))


    # Custom functions

    def get_space(self):
        attrs = gym.spaces.Box(low=[0, 0, 0, 0, 0, 0, 0, 0, 50], high=[1, 1, 1, 1, 1, 1, 1, 255, 100])
        mode = gym.spaces.Discrete(2)

        return gym.spaces.Tuple([attrs, mode])

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
        if not self.sp.currently_playing()['is_playing']:
            self.sp.start_playback()

        self.p.add_to_queue(uri)

        if now:
            self.seek_song(uri)

    def play_similar(self, target_attrs, tempo, mode, now=True):
        recs = self.sp.recommendations(
            seed_artists=self.config['SeedArtists'].values(),
            seed_genres=self.config['SeedArtists'].keys(),
            seed_tracks=self.config['SeedTracks'].values(),
            target_acousticness=target_attrs[0],
            target_danceability=target_attrs[1],
            target_energy=target_attrs[2],
            target_liveness=target_attrs[3],
            target_loudness=target_attrs[4],
            target_speechiness=target_attrs[5],
            target_valence=target_attrs[6],
            target_tempo=tempo,
            target_mode=mode
        )

        for track in recs['tracks']:
            if track['uri'] in self.uri_set:
                continue
            else:
                self.play_song(track['uri'], now=now)
                self.uri_set.add(track['uri'])
                break
        else:
            raise Exception()

    def new_song_needed(self):
        playback = self.sp.current_playback()

        to_end = playback['item']['duration_ms'] - playback['progress_ms']

        return to_end * 1000 > self.INTERVAL
