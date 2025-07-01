"""
Test connection error handling in SpotifyConnector.

This test verifies that the SpotifyConnector properly handles network errors
and doesn't get stuck in infinite retry loops.
"""

import datetime as dt
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout

from spotifyconnector.connector import (CredentialsExpired,
                                        MaxRetriesException, SpotifyConnector)


class TestConnectionHandling:
    """Test connection error handling in SpotifyConnector."""

    def test_connection_error_retries_and_fails(self, spotify_connector):
        """Test that ConnectionError is retried and eventually raises exception."""
        with patch("requests.Session.send") as mock_send:
            # Mock a persistent connection error
            mock_send.side_effect = ConnectionError(
                "Failed to establish a new connection: [Errno -3] Temporary failure in name resolution"
            )

            with patch.object(spotify_connector, "_ensure_auth"):
                with pytest.raises(ConnectionError):
                    spotify_connector._request("https://test.example.com/test")

                # Should have retried MAX_REQUEST_ATTEMPTS times
                assert mock_send.call_count == 6  # MAX_REQUEST_ATTEMPTS

    def test_timeout_error_retries_and_fails(self, spotify_connector):
        """Test that Timeout errors are retried and eventually raise exception."""
        with patch("requests.Session.send") as mock_send:
            mock_send.side_effect = Timeout("Request timed out")

            with patch.object(spotify_connector, "_ensure_auth"):
                with pytest.raises(Timeout):
                    spotify_connector._request("https://test.example.com/test")

                assert mock_send.call_count == 6

    def test_authentication_skipped_on_network_errors(self, spotify_connector):
        """Test that authentication is skipped after network errors to prevent infinite loops."""
        with patch("requests.Session.send") as mock_send:
            mock_send.side_effect = ConnectionError("Network error")

            with patch.object(spotify_connector, "_ensure_auth") as mock_auth:
                with pytest.raises(ConnectionError):
                    spotify_connector._request("https://test.example.com/test")

                # _ensure_auth should only be called once (on first attempt)
                assert mock_auth.call_count == 1

    def test_successful_request_after_network_error(self, spotify_connector):
        """Test that requests can succeed after initial network errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {"test": "data"}

        with patch("requests.Session.send") as mock_send:
            # First two attempts fail, third succeeds
            mock_send.side_effect = [
                ConnectionError("Network error"),
                ConnectionError("Network error"),
                mock_response,
            ]

            with patch.object(spotify_connector, "_ensure_auth"):
                result = spotify_connector._request("https://test.example.com/test")

                assert result == {"test": "data"}
                assert mock_send.call_count == 3

    def test_http_errors_still_handled_correctly(self, spotify_connector):
        """Test that HTTP errors (non-network) are still handled as before."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.ok = False
        mock_response.headers = {}
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")

        with patch("requests.Session.send", return_value=mock_response):
            with patch.object(spotify_connector, "_ensure_auth"):
                with pytest.raises(HTTPError):
                    spotify_connector._request("https://test.example.com/test")

    def test_503_errors_are_retried(self, spotify_connector):
        """Test that 503 errors are retried with exponential backoff."""
        mock_response_503 = Mock()
        mock_response_503.status_code = 503
        mock_response_503.ok = False

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.ok = True
        mock_response_200.json.return_value = {"test": "data"}

        with patch("requests.Session.send") as mock_send:
            # First attempt returns 503, second succeeds
            mock_send.side_effect = [mock_response_503, mock_response_200]

            with patch.object(spotify_connector, "_ensure_auth"):
                with patch("spotifyconnector.connector.sleep") as mock_sleep:
                    result = spotify_connector._request("https://test.example.com/test")

                    assert result == {"test": "data"}
                    assert mock_send.call_count == 2
                    mock_sleep.assert_called_once()  # Should sleep between retries

    def test_authenticate_handles_connection_errors(self, spotify_connector):
        """Test that _authenticate method properly handles connection errors."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = ConnectionError("DNS resolution failed")

            # Should eventually raise RetryError after retries (tenacity wraps the ConnectionError)
            with pytest.raises(Exception) as exc_info:  # Catch any exception type
                spotify_connector._authenticate()

            # The exception should be related to connection/retry errors
            assert "ConnectionError" in str(exc_info.value) or "RetryError" in str(
                exc_info.value
            )

    def test_max_retries_exception_with_network_error(self, spotify_connector):
        """Test MaxRetriesException details when network errors occur."""
        with patch("requests.Session.send") as mock_send:
            mock_send.side_effect = ConnectionError("Network unreachable")

            with patch.object(spotify_connector, "_ensure_auth"):
                with pytest.raises(ConnectionError) as exc_info:
                    spotify_connector._request("https://test.example.com/test")

                # Should re-raise the original ConnectionError, not MaxRetriesException
                assert "Network unreachable" in str(exc_info.value)

    def test_aggregate_method_with_connection_error(
        self, spotify_connector, sample_dates
    ):
        """Test that the aggregate method properly handles connection errors."""
        with patch.object(spotify_connector, "_request") as mock_request:
            mock_request.side_effect = ConnectionError("DNS failure")

            with pytest.raises(ConnectionError):
                spotify_connector.aggregate(sample_dates["start"])

            # Verify the correct URL was constructed
            expected_url = f"{spotify_connector.base_url}/shows/{spotify_connector.podcast_id}/aggregate"
            mock_request.assert_called_once_with(
                expected_url, params={"start": "2025-06-28", "end": "2025-06-28"}
            )

    def test_exponential_backoff_timing(self, spotify_connector):
        """Test that exponential backoff increases delay properly."""
        with patch("requests.Session.send") as mock_send:
            mock_send.side_effect = ConnectionError("Network error")

            with patch.object(spotify_connector, "_ensure_auth"):
                with patch("spotifyconnector.connector.sleep") as mock_sleep:
                    with pytest.raises(ConnectionError):
                        spotify_connector._request("https://test.example.com/test")

                    # Check that sleep was called with increasing delays
                    sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]

                    # Should have exponential backoff: 4.0, 8.0, 16.0, 32.0, 64.0
                    expected_delays = [
                        4.0,
                        8.0,
                        16.0,
                        32.0,
                        64.0,
                    ]  # delay *= 2 before sleep
                    assert len(sleep_calls) == 5  # 5 sleeps for 6 attempts
                    assert sleep_calls == expected_delays

    def test_bearer_token_preserved_during_network_errors(self, spotify_connector):
        """Test that bearer token is not cleared during network errors."""
        # Set up a mock bearer token
        spotify_connector._bearer = "test_bearer_token"
        spotify_connector._bearer_expires = dt.datetime.now() + dt.timedelta(hours=1)

        with patch("requests.Session.send") as mock_send:
            mock_send.side_effect = ConnectionError("Network error")

            original_bearer = spotify_connector._bearer

            with pytest.raises(ConnectionError):
                spotify_connector._request("https://test.example.com/test")

            # Bearer token should still be there
            assert spotify_connector._bearer == original_bearer


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
