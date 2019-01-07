FROM python:alpine

ENV SPOTIPY_CLIENT_ID ""
ENV SPOTIPY_CLIENT_SECRET ""
ENV PLEX_URL ""
ENV PLEX_TOKEN ""
ENV SPOTIFY_URIS ""

WORKDIR /app/

RUN source env/bin/activate && \
    pip install requests && \
    pip install requests

COPY spotify-sync.py /app/spotify-sync.py

CMD spotify-sync.py