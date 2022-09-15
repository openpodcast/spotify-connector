import json
from loguru import logger
from .connector import SpotifyConnector

# To use the library as a script, fetch the config from the environment
import os
BASE_URL = os.environ.get("SPOTIFY_BASE_URL")
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
PODCAST_ID = os.environ.get("SPOTIFY_PODCAST_ID")
SP_DC = os.environ.get("SPOTIFY_SP_DC")
SP_KEY = os.environ.get("SPOTIFY_SP_KEY")

connector = SpotifyConnector(
    base_url=BASE_URL,
    client_id=CLIENT_ID,
    podcast_id=PODCAST_ID,
    sp_dc=SP_DC,
    sp_key=SP_KEY,
)

# Fetch metadata for podcast
meta = connector.metadata()
logger.info("Podcast Metadata = {}", json.dumps(meta, indent=4))

# Fetch stream data for podcast
# end  = dt.datetime.now()
# start = dt.datetime.now() - dt.timedelta(days=7)
# streams = connector.streams("48DAya24YOjS7Ez49JSH3y", start, end)
# logger.info("Podcast Streams = {}", json.dumps(streams, indent=4))

# Fetch listener data for podcast
# end  = dt.datetime.now()
# start = dt.datetime.now() - dt.timedelta(days=7)
# listeners = connector.listeners("48DAya24YOjS7Ez49JSH3y", start, end)
# logger.info("Podcast Listeners = {}", json.dumps(listeners, indent=4))

# Fetch aggregate data for podcast
# end  = dt.datetime.now()
# start = dt.datetime.now() - dt.timedelta(days=7)
# aggregate  = connector.aggregate("48DAya24YOjS7Ez49JSH3y", start, end)
# logger.info("Podcast Aggregate = {}", json.dumps(aggregate, indent=4))

# Fetch episode data for podcast
# end  = dt.datetime.now()
# start = dt.datetime.now() - dt.timedelta(days=7)
# episodes = connector.episodes(start, end)
# logger.info("Podcast Episodes = {}", json.dumps(episodes, indent=4))