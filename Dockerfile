FROM python:alpine

ENV SPOTIPY_CLIENT_ID ""
ENV SPOTIPY_CLIENT_SECRET ""
ENV PLEX_URL ""
ENV PLEX_TOKEN ""
ENV SPOTIFY_URIS ""
ENV SECONDS_TO_WAIT 1800

WORKDIR /app/

COPY spotify-sync.py /app/spotify-sync.py
COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

CMD python spotify-sync.py