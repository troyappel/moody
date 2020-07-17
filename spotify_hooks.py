import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dataclasses import dataclass

INTERVAL=30

import configparser

config = configparser.ConfigParser(allow_no_value=True)

uri_set = set()

scope = "user-read-currently-playing user-read-playback-state streaming"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope,
    client_id=config['SPOTIFY']['CLIENT_ID'],
    client_secret=config['SPOTIFY']['CLIENT_SECRET'],
    redirect_uri=config['SPOTIFY']['REDIRECT_URI'],
    username=config['SPOTIFY']['USERNAME']
))

def init():
    config.read("config.txt")
    config_ids()



def config_ids():
    artists = config['SeedArtists'].keys()
    tracks = config['SeedTracks'].keys()

    for artist in artists:
        if config['SeedArtists'][artist]:
            continue
        results = sp.search(q='artist:' + artist, type='artist')
        config['SeedArtists'][artist] = results['artists']['items'][0]['id']

    for track in tracks:
        if config['SeedTracks'][track]:
            continue
        results = sp.search(q='track:' + track, type='track')
        config['SeedTracks'][track] = results['tracks']['items'][0]['id']

    with open('config.txt', 'w') as configfile:
        config.write(configfile)



def seek_song(uri):
    prev_uri = None

    # Need to time out if we see playing song is not changing -- happens if there are duplicate things
    try_count = 0

    while(True):
        cur_uri = sp.currently_playing()['item']['uri']
        print(prev_uri, cur_uri, uri)
        if cur_uri == uri:
            break
        elif cur_uri == prev_uri:
            if try_count > 5:
                sp.next_track()
                try_count = 0
            try_count += 1
            time.sleep(1)
            continue
        else:
            try_count = 0
            prev_uri = cur_uri
            time.sleep(3)
            sp.next_track()


def play_song(uri, now=True):
    if not sp.currently_playing()['is_playing']:
        sp.start_playback()

    sp.add_to_queue(uri)

    if(now):
        seek_song(uri)

def play_similar(target_attrs, tempo, mode, now=True):
    recs = sp.recommendations(
        seed_artists=config['SeedArtists'].values(),
        seed_genres=config['SeedArtists'].keys(),
        seed_tracks=config['SeedTracks'].values(),
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
        if track['uri'] in uri_set:
            continue
        else:
            play_song(track['uri'], now=now)
            uri_set.add(track['uri'])
            break
    else:
        raise Exception()


def get_cur_song():
    return sp.current_playback()['item']


def new_song_needed():
    playback = sp.current_playback()

    to_end = playback['item']['duration_ms'] - playback['progress_ms']

    return to_end * 1000 > INTERVAL
