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

    # If podcast ID is not provided, fetch catalog of podcasts
    if not connector.podcast_id:
        catalog = connector.catalog()
        logger.info("Podcast Catalog = {}", json.dumps(catalog, indent=4))
        return

    # Fetch metadata for podcast
    meta = connector.metadata()
    logger.info("Podcast Metadata = {}", json.dumps(meta, indent=4))

    # Fetch streams for podcast
    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=7)
    streams = connector.streams(start, end)
    logger.info("Podcast Streams = {}", json.dumps(streams, indent=4))

    # Fetch followers for podcast
    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=1)
    followers = connector.followers(start, end)
    logger.info("Podcast Followers = {}", json.dumps(followers, indent=4))

    # Fetch aggregate data for podcast
    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=1)
    aggregate = connector.aggregate(start, end)
    logger.info("Podcast Aggregate = {}", json.dumps(aggregate, indent=4))

    # Fetch podcast episodes
    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=4)
    # Get all episodes from generator
    for episode in connector.episodes(start, end):
        logger.info("Episode = {}", json.dumps(episode, indent=4))

    # Fetch metadata for single podcast episode
    episode_meta = connector.metadata(episode=episode["id"])
    logger.info("Episode Streams = {}", json.dumps(episode_meta, indent=4))

    # Fetch stream data for single podcast episode
    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=7)
    streams = connector.streams(start, end, episode=episode["id"])
    logger.info("Episode Streams = {}", json.dumps(streams, indent=4))

    # Fetch listener data for single podcast episode
    start = dt.datetime.now() - dt.timedelta(days=4)
    end = dt.datetime.now() - dt.timedelta(days=1)
    listeners = connector.listeners(
        start, end, episode=episode["id"])
    logger.info("Episode = {} Listeners = {}", episode["id"], json.dumps(listeners, indent=4))

    # Fetch aggregate data for single podcast episode
    end = dt.datetime.now()
    start = dt.datetime.now() - dt.timedelta(days=7)
    aggregate = connector.aggregate(start, end, episode=episode["id"])
    logger.info("Episode Aggregate = {}", json.dumps(aggregate, indent=4))

    # Fetch performance data for single podcast episode
    performance = connector.performance(episode["id"])
    logger.info("Episode Performance = {}", json.dumps(performance, indent=4))


if __name__ == "__main__":
    main()
