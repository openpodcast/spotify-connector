import json
from loguru import logger
from .connector import SpotifyConnector
import os
import datetime as dt


def main():
    # To use the library as a script, fetch the config from the environment
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

    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=7)
    streams = connector.streams(start, end)
    logger.info("Podcast Streams = {}", json.dumps(streams, indent=4))

    # Fetch episodes
    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=7)
    # Get all episodes from iterator
    for episode in connector.episodes(start, end):
        logger.info("Episode = {}", json.dumps(episode, indent=4))

    # Fetch metadata for podcast episode
    episode_meta = connector.metadata(episode="48DAya24YOjS7Ez49JSH3y")
    logger.info("Episode Streams = {}", json.dumps(episode_meta, indent=4))

    # Fetch stream data for podcast episode
    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=7)
    streams = connector.streams(start, end, episode="48DAya24YOjS7Ez49JSH3y")
    logger.info("Episode Streams = {}", json.dumps(streams, indent=4))

    # Fetch listener data for podcast episode
    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=7)
    listeners = connector.listeners(start, end, episode="48DAya24YOjS7Ez49JSH3y")
    logger.info("Podcast Listeners = {}", json.dumps(listeners, indent=4))

    # Fetch aggregate data for podcast episode
    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=7)
    aggregate = connector.aggregate(start, end, episode="48DAya24YOjS7Ez49JSH3y")
    logger.info("Podcast Aggregate = {}", json.dumps(aggregate, indent=4))

    # Fetch performance data for podcast episode
    performance = connector.performance("48DAya24YOjS7Ez49JSH3y")
    logger.info("Podcast Performance = {}", json.dumps(performance, indent=4))


if __name__ == "__main__":
    main()
