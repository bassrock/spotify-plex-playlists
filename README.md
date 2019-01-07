Spotify -> Plex
-
[![](https://img.shields.io/docker/automated/bassrock/spotify-plex-playlists.svg)](https://cloud.docker.com/repository/docker/bassrock/spotify-plex-playlists) [![](https://img.shields.io/docker/pulls/bassrock/spotify-plex-playlists.svg)](https://img.shields.io/docker/pulls/bassrock/spotify-plex-playlists.svg) [![](https://img.shields.io/docker/stars/bassrock/spotify-plex-playlists.svg)](https://cloud.docker.com/repository/docker/bassrock/spotify-plex-playlists)

Converts Spotify URI's to Plex Playlists on a Specified Interval.

Setup
----
Set the following Docker environment variables

`SPOTIPY_CLIENT_ID` - A Spotify client id created here: https://developer.spotify.com/dashboard/login

`SPOTIPY_CLIENT_SECRET` - The Spotify client secret from the created client id

`PLEX_URL` - Your plex url: `http://plex:32400`

`PLEX_TOKEN` - Your plex token found by https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

`SPOTIFY_URIS` - A comma seperated list of the spotify URI's you would like to import: `spotify:user:sonosplay,spotify:user:sonosplay:playlist:6nQjiSQhdf84s2AAxweRBv`

`SECONDS_TO_WAIT` - How many seconds to wait before syncs

The following URI's are supported:
* A user's URI which will import all public playlists a user owns: `spotify:user:sonosplay`
* A playlist URI which imports a specific playlist (must be public): `spotify:user:sonosplay:playlist:6nQjiSQhdf84s2AAxweRBv`

Playlists will only be created on Plex if your Plex instance has at least one of the songs. Only songs found on your Plex will be created in the Plex Playlilst
