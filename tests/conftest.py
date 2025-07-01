"""
Shared pytest fixtures and configuration for SpotifyConnector tests.
"""

import pytest

from spotifyconnector.connector import SpotifyConnector


@pytest.fixture
def spotify_connector():
    """Create a SpotifyConnector instance for testing."""
    return SpotifyConnector(
        base_url="https://generic.wg.spotify.com/podcasters/v0",
        client_id="test_client_id",
        podcast_id="test_podcast_id",
        sp_dc="test_sp_dc",
        sp_key="test_sp_key",
    )


@pytest.fixture
def mock_bearer_token():
    """Mock bearer token for testing."""
    return "mock_bearer_token_12345"


@pytest.fixture
def sample_dates():
    """Sample date range for testing."""
    import datetime as dt

    return {
        "start": dt.date(2025, 6, 28),
        "end": dt.date(2025, 6, 29),
        "single": dt.date(2025, 6, 28),
    }
