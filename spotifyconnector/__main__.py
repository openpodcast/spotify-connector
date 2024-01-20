"""
Command line interface to run the Spotify Connector
"""

import json
import os
import datetime as dt

from loguru import logger

from .connector import SpotifyConnector


def now():
    """
    Returns the current datetime object.
    """
    return dt.datetime.now()


def days_ago(days):
    """
    Returns a datetime object representing the time 'days' days ago from now.
    """
    return now() - dt.timedelta(days=days)


def execute_and_log(endpoint_name, func, *args, **kwargs):
    """
    Execute a function and log the result
    """
    try:
        result = func(*args, **kwargs)
        log_status(endpoint_name, True, result)
        return result
    except Exception as error:  # pylint: disable=broad-except
        log_status(endpoint_name, False, {"error": str(error)})
        return None


def log_status(endpoint_name, status, data):
    """
    Log the status of an endpoint
    """
    symbol = "✓" if status else "✗"
    logger.info(f"{symbol} {endpoint_name}: {json.dumps(data, separators=(',', ':'))}")


def main():  # pylint: disable=too-many-locals
    """
    Main entrypoint to run the connector
    """
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

    if not connector.podcast_id:
        execute_and_log("catalog", connector.catalog)
        return

    execute_and_log("metadata", connector.metadata)

    execute_and_log("streams", connector.streams, days_ago(7), now())

    execute_and_log("followers", connector.followers, days_ago(1), now())

    execute_and_log("impressions_total", connector.impressions, "total")

    execute_and_log("impressions_total", connector.impressions, "total", days_ago(60))

    execute_and_log(
        "impressions_daily", connector.impressions, "daily", days_ago(14), now()
    )

    execute_and_log(
        "impressions_faceted", connector.impressions, "faceted", days_ago(14), now()
    )

    execute_and_log("aggregate", connector.aggregate, days_ago(1), now())

    episodes = connector.episodes(days_ago(4), now())
    for episode in episodes:
        logger.info("Episode = {}", json.dumps(episode, separators=(",", ":")))

        execute_and_log("episode_metadata", connector.metadata, episode=episode["id"])

        execute_and_log(
            "episode_streams",
            connector.streams,
            days_ago(7),
            now(),
            episode=episode["id"],
        )

        execute_and_log(
            "episode_listeners",
            connector.listeners,
            days_ago(4),
            days_ago(1),
            episode=episode["id"],
        )

        execute_and_log(
            "episode_aggregate",
            connector.aggregate,
            days_ago(7),
            now(),
            episode=episode["id"],
        )

        execute_and_log(
            "episode_performance", connector.performance, episode=episode["id"]
        )


if __name__ == "__main__":
    main()
