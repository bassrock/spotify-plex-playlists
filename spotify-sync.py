import re
import time
import logging
from plexapi.server import PlexServer
from plexapi.audio import Track
import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List


def filterPlexArray(plexItems=[], song="", artist="") -> List[Track]:
    for item in list(plexItems):
        if type(item) is not Track:
            plexItems.remove(item)
            continue
        if item.title.lower() != song.lower():
            plexItems.remove(item)
            continue
        artistItem = item.artist()
        if str(item.originalTitle).lower() != artist.lower() and artistItem.title.lower() != artist.lower():
            plexItems.remove(item)
            continue

    return plexItems


def getSpotifyPlaylist(sp: spotipy.client, userId: str, playlistId: str) -> []:
    playlist = sp.user_playlist(userId, playlistId)
    return playlist


# Returns a list of spotify playlist objects
def getSpotifyUserPlaylists(sp: spotipy.client, userId: str) -> []:
    playlists = sp.user_playlists(userId)
    spotifyPlaylists = []
    while playlists:
        playlistItems = playlists['items']
        for i, playlist in enumerate(playlistItems):
            if playlist['owner']['id'] == userId:
                spotifyPlaylists.append(getSpotifyPlaylist(sp, userId, playlist['id']))
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return spotifyPlaylists


def getSpotifyTracks(sp: spotipy.client, playlist: []) -> []:
    spotifyTracks = []
    tracks = playlist['tracks']
    spotifyTracks.extend(tracks['items'])
    while tracks['next']:
        tracks = sp.next(tracks)
        spotifyTracks.extend(tracks['items'])
    return spotifyTracks


def getPlexTracks(plex: PlexServer, spotifyTracks: []) -> List[Track]:
    plexTracks = []
    for spotifyTrack in spotifyTracks:
        track = spotifyTrack['track']
        track_options = [track['name']]
        
        # Parse remixes properly
        mix_search = re.search('(.*) - (.*Remix|Original Mix)', track_options[0], re.IGNORECASE)
        if mix_search:
            track_options[0] = mix_search.group(1) + ' (' + mix_search.group(2) + ')'
            # Also match the track without "Original Mix" as this is rarely specified except in Spotify
            if mix_search.group(2) == "Original Mix":
                track_options.append(mix_search.group(1))

        logging.info("Searching Plex for: %s by %s" % (track_options[0], track['artists'][0]['name']))

        for track_name in track_options:
            for artist in track['artists']:
                try:
                    musicTracks = plex.search(track_name, mediatype='track')
                except:
                    try:
                        musicTracks = plex.search(track_name, mediatype='track')
                    except:
                        logging.info("Issue making plex request")
                        break
                if len(musicTracks) > 0:
                    plexMusic = filterPlexArray(musicTracks, track_name, artist['name'])
                    if len(plexMusic) > 0:
                        logging.info("Found Plex Song: %s by %s" % (track_name, artist['name']))
                        plexTracks.append(plexMusic[0])
                        break
                    
    return plexTracks


def createPlaylist(plex: PlexServer, sp: spotipy.Spotify, playlist: []):
    playlistName = playlist['owner']['id'] + " - " + playlist['name']
    logging.info('Starting playlist %s' % playlistName)
    plexTracks = getPlexTracks(plex, getSpotifyTracks(sp, playlist))
    if len(plexTracks) > 0:
        try:
            plexPlaylist = plex.playlist(playlistName)
            logging.info('Updating playlist %s' % playlistName)
            plexPlaylist.addItems(plexTracks)
        except:
            logging.info("Creating playlist %s" % playlistName)
            plex.createPlaylist(playlistName, plexTracks)

def parseSpotifyURI(uriString: str) -> {}:
    spotifyUriStrings = re.sub(r'^spotify:', '', uriString).split(":")
    spotifyUriParts = {}
    for i, string in enumerate(spotifyUriStrings):
        if i % 2 == 0:
            spotifyUriParts[spotifyUriStrings[i]] = spotifyUriStrings[i+1]

    return spotifyUriParts


def runSync(plex : PlexServer, sp : spotipy.Spotify, spotifyURIs: []):
    logging.info('Starting a Sync Operation')
    playlists = []

    for spotifyUriParts in spotifyURIs:
        if 'user' in spotifyUriParts.keys() and 'playlist' not in spotifyUriParts.keys():
            logging.info('Getting playlists for %s' % spotifyUriParts['user'])
            playlists.extend(getSpotifyUserPlaylists(sp, spotifyUriParts['user']))
        elif 'user' in spotifyUriParts.keys() and 'playlist' in spotifyUriParts.keys():
            logging.info('Getting playlist %s from user %s' % (spotifyUriParts['user'], spotifyUriParts['playlist']))
            playlists.append(getSpotifyPlaylist(sp, spotifyUriParts['user'], spotifyUriParts['playlist']))

    for playlist in playlists:
        createPlaylist(plex, sp, playlist)
    logging.info('Finished a Sync Operation')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    spotifyUris = os.environ.get('SPOTIFY_URIS')

    if spotifyUris is None:
        logging.error("No spotify uris")

    secondsToWait = int(os.environ.get('SECONDS_TO_WAIT', 1800))
    baseurl = os.environ.get('PLEX_URL')
    token = os.environ.get('PLEX_TOKEN')
    plex = PlexServer(baseurl, token)

    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    spotifyUris = spotifyUris.split(",")


    spotifyMainUris = []

    for spotifyUri in spotifyUris:
        spotifyUriParts = parseSpotifyURI(spotifyUri)
        spotifyMainUris.append(spotifyUriParts)

    while True:
        runSync(plex, sp, spotifyMainUris)
        time.sleep(secondsToWait)
