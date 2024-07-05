# flake8: noqa: C0114, R0801
import os
from spotifyconnector import SpotifyConnector

base_url = os.environ.get("SPOTIFY_BASE_URL")
client_id = os.environ.get("SPOTIFY_CLIENT_ID")
podcast_id = os.environ.get("SPOTIFY_PODCAST_ID")
sp_dc = os.environ.get("SPOTIFY_SP_DC")
sp_key = os.environ.get("SPOTIFY_SP_KEY")

connector = SpotifyConnector(
    base_url,
    client_id,
    podcast_id,
    sp_dc,
    sp_key,
)

catalog = connector.catalog()

for show in catalog["shows"]:
    print(f"Show Name: {show['name']}")
    print(f"Show ID: {show['id']}")
    print("\n")
