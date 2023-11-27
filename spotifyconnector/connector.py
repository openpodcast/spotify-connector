"""
This module provides a class to connect to an unofficial Spotify API
that provides podcast analytics. It relies on using cookies generated
manually by logging in with the appropriate user at podcasters.spotify.com.

Cookies supposedly last 1 year.
"""

import random
import string
import base64
import hashlib
import re
from typing import Dict, Optional
import datetime as dt
from time import sleep
from threading import RLock
from loguru import logger
import requests
from requests.exceptions import HTTPError
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_exponential
from tenacity.retry import retry_if_exception_type
import yaml

DELAY_BASE = 2.0
MAX_REQUEST_ATTEMPTS = 6


class CredentialsExpired(Exception):
    """
    CredentialsExpired is raised when the Spotify API asks for a login
    This is usually because the cookies have expired.
    """


def random_string(
    length: int,
    chars: str = string.ascii_lowercase + string.ascii_uppercase + string.digits,
) -> str:
    """
    Simple helper function to generate random strings suitable for use with Spotify
    """
    return "".join(random.choices(chars, k=length))


class MaxRetriesException(Exception):
    """
    Raised when the maximum number of retries is reached
    """

    def __init__(self, url, last_status_code, attempts):
        super().__init__(
            f"All retries failed for URL {url}. "
            f"Last status code: {last_status_code}. "
            f"Attempts: {attempts}"
        )


class SpotifyConnector:
    """Representation of the inofficial Spotify podcast API."""

    def __init__(
        self,
        base_url,
        client_id,
        podcast_id,
        sp_dc,
        sp_key,
    ):
        """Initializes the SpotifyConnector object.

        Args:
            base_url (str): Base URL for the API.
            client_id (str): Spotify Client ID for the API.
            podcast_id (str): Spotify Podcast ID for the API.
            sp_dc (str): Spotify cookie.
            sp_key (str): Spotify cookie.
        """

        self.base_url = base_url
        self.client_id = client_id
        self.podcast_id = podcast_id
        self.sp_dc = sp_dc
        self.sp_key = sp_key

        self._bearer: Optional[str] = None
        self._bearer_expires: Optional[dt.datetime] = None
        self._auth_lock = RLock()
        # Flag to indicate that auth has failed and we should not retry
        # (to avoid spamming Spotify with requests and risking a ban)
        self._auth_poisoned = False

    @retry(
        retry=retry_if_exception_type(HTTPError),
        wait=wait_exponential(),
        stop=stop_after_attempt(7),
    )
    def _authenticate(self):
        """
        Retrieves a Bearer token for the inofficial Spotify API, valid 1 hour.

        Generally follows the steps outlined here:
        https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
        (with a few exceptions)
        """
        if self._auth_poisoned:
            raise CredentialsExpired(
                "Authentication has failed, not retrying. "
                "Check credentials and try again."
            )

        with self._auth_lock:
            logger.info("Retrieving Bearer")

            logger.debug("Generating secrets")

            state = random_string(32)

            code_verifier = random_string(64)
            code_challenge = base64.b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            ).decode("utf-8")

            # Fix up format of code_challenge for spotify
            code_challenge = re.sub(r"=+$", "", code_challenge)
            code_challenge = code_challenge.replace("/", "_")
            code_challenge = code_challenge.replace("+", "-")

            logger.trace("state = {}", state)
            logger.trace("code_verifier = {}", code_verifier)
            logger.trace("code_challenge = {}", code_challenge)

            logger.debug("Requesting User Authorization")
            response = requests.get(
                "https://accounts.spotify.com/oauth2/v2/auth",
                params={
                    "response_type": "code",
                    "client_id": self.client_id,
                    "scope": (
                        "streaming ugc-image-upload user-read-email "
                        "user-read-private"
                    ),
                    "redirect_uri": "https://podcasters.spotify.com",
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256",
                    "state": state,
                    "response_mode": "web_message",
                    "prompt": "none",
                },
                cookies={
                    "sp_dc": self.sp_dc,
                    "sp_key": self.sp_key,
                },
                timeout=60,
            )
            logger.trace("response - {}", response.text)

            # Raise an exception if we get a 4xx or 5xx response
            response.raise_for_status()

            # We get some weird HTML here that contains some JS
            html = response.text

            logger.trace("html = {}", html)

            # At this point, we should have an HTTP response,
            # but it could be an error page, containing an error message like
            # response: {
            #   "error": "login_required",
            #   "state": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            # }
            # Check for this error case and raise an exception if we find it
            # to avoid getting stuck in a loop
            if "login_required" in html:
                self._auth_poisoned = True
                raise CredentialsExpired("Login required (credentials cookie expired?)")

            match = re.search(r"const authorizationResponse = (.*?);", html, re.DOTALL)
            json_str = match.group(1)

            # The extracted string isn't strictly valid JSON due to some missing quotes,
            # but PyYAML loads it fine
            auth_response = yaml.safe_load(json_str)

            # Confirm that auth was successful
            assert auth_response["type"] == "authorization_response"
            assert auth_response["response"]["state"] == state

            auth_code = auth_response["response"]["code"]

            logger.trace("auth_code = {}", auth_code)

            logger.debug("Requesting Bearer Token")
            response = requests.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "code": auth_code,
                    "redirect_uri": "https://podcasters.spotify.com",
                    "code_verifier": code_verifier,
                },
                timeout=60,
            )
            response.raise_for_status()

            response_json = response.json()

            self._bearer = response_json["access_token"]
            expires_in = response_json["expires_in"]
            self._bearer_expires = dt.datetime.now() + dt.timedelta(seconds=expires_in)

            logger.trace("bearer = {}", self._bearer)

            logger.success("Bearer token retrieved!")

    def _ensure_auth(self):
        """Checks if Bearer token expires soon. If so, requests a new one."""

        with self._auth_lock:
            if self._bearer is None or self._bearer_expires < (
                dt.datetime.now() - dt.timedelta(minutes=5)
            ):
                self._authenticate()

    def _build_url(self, *path: str) -> str:
        return f"{self.base_url}/{'/'.join(path)}"

    @staticmethod
    def _date_params(start: dt.date, end: dt.date) -> Dict[str, str]:
        # Only format the date, not the time
        return {
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
        }

    def _request(self, url: str, *, params: Optional[Dict[str, str]] = None) -> dict:
        logger.trace("url = {}", url)
        delay = DELAY_BASE

        last_status_code = None
        for attempt in range(MAX_REQUEST_ATTEMPTS):
            self._ensure_auth()

            # Create request object with requests and trace it before sending
            request = requests.Request(
                "GET",
                url,
                params=params,
                headers={"Authorization": f"Bearer {self._bearer}"},
            )
            prepared_request = request.prepare()
            logger.trace("request - {}", prepared_request.url)
            response = requests.Session().send(prepared_request)

            if response.status_code in (429, 502, 503, 504):
                delay *= 2
                logger.log(
                    ("INFO" if attempt < 3 else "WARNING"),
                    'Got {} for URL "{}", next delay: {}s',
                    response.status_code,
                    url,
                    delay,
                )
                sleep(delay)
                continue

            if response.status_code == 401:
                self._authenticate()
                continue

            if not response.ok:
                logger.error("Error in API:")
                logger.info(response.status_code)
                logger.info(response.headers)
                logger.info(response.text)
                response.raise_for_status()

            logger.trace("response = {}", response.text)
            return response.json()

        raise MaxRetriesException(url, last_status_code, MAX_REQUEST_ATTEMPTS)

    def metadata(self, episode=None) -> dict:
        """Loads metadata for podcast.

        Args:
            episode (str): ID of the episode to request data for (optional).
              If this is not provided, data for all episodes will be returned.

        Returns:
            dict: Response data from API.
        """
        if episode is None:
            url = self._build_url(
                "shows",
                self.podcast_id,
                "metadata",
            )
        else:
            url = self._build_url(
                "episodes",
                episode,
                "metadata",
            )
        return self._request(url)

    def streams(
        self,
        start: dt.date,
        end: Optional[dt.date] = None,
        episode=None,
    ) -> dict:
        """Loads podcast/episode stream data, which includes the number of
        starts and completions for each episode.

        Args:
            start (dt.date): Earliest date to request data for.
            end (Optional[dt.date], optional): Most recent date to request data for.
              Defaults to None. Will be set to ``start`` if None.
            episode (str): ID of the episode to request data for (optional).
              If this is not provided, data for all episodes will be returned.

        Returns:
            dict: [description]
        """
        if end is None:
            end = start

        if episode is None:
            url = self._build_url(
                "shows",
                self.podcast_id,
                "detailedStreams",
            )
        else:
            url = self._build_url(
                "episodes",
                episode,
                "detailedStreams",
            )
        return self._request(url, params=self._date_params(start, end))

    def listeners(
        self,
        start: dt.date,
        end: Optional[dt.date] = None,
        episode=None,
    ) -> dict:
        """Loads podcast listener data, which includes the number of
        listeners for each episode.

        Args:
            start (dt.date): Earliest date to request data for.
            end (Optional[dt.date], optional): Most recent date to request data for.
              Defaults to None. Will be set to ``start`` if None.
            episode (str): ID of the episode to request data for (optional).
              If this is not provided, data for all episodes will be returned.

        Returns:
            dict: [description]
        """
        if end is None:
            end = start

        if episode is None:
            url = self._build_url(
                "shows",
                self.podcast_id,
                "listeners",
            )
        else:
            url = self._build_url(
                "episodes",
                episode,
                "listeners",
            )
        return self._request(url, params=self._date_params(start, end))

    def followers(
        self,
        start: dt.date,
        end: Optional[dt.date] = None,
    ) -> dict:
        """Loads podcast follower data.

        Args:
            start (dt.date): Earliest date to request data for.
            end (Optional[dt.date], optional): Most recent date to request data for.
              Defaults to None. Will be set to ``start`` if None.

        Returns:
            dict: [description]
        """
        if end is None:
            end = start

        url = self._build_url(
            "shows",
            self.podcast_id,
            "followers",
        )
        return self._request(url, params=self._date_params(start, end))

    def aggregate(
        self,
        start: dt.date,
        end: Optional[dt.date] = None,
        episode=None,
    ) -> dict:
        """Loads podcast aggregate data, which includes the number of
        starts and completions for each episode.

        Args:
            start (dt.date): Earliest date to request data for.
            end (Optional[dt.date], optional): Most recent date to request data for.
              Defaults to None. Will be set to ``start`` if None.
            episode (str): ID of the episode to request data for (optional).
              If this is not provided, data for all episodes will be returned.

        Returns:
            dict: [aggregate]
        """
        if end is None:
            end = start

        if episode is None:
            url = self._build_url(
                "shows",
                self.podcast_id,
                "aggregate",
            )
        else:
            url = self._build_url(
                "episodes",
                episode,
                "aggregate",
            )
        return self._request(url, params=self._date_params(start, end))

    def episodes(
        self,
        start: dt.date,
        end: Optional[dt.date] = None,
        page: int = 1,
        size: int = 50,
        sort_by: str = "releaseDate",
        sort_order: str = "descending",
        filter_by: str = "",
    ) -> dict:
        """Loads podcast episode data, which includes the number of
        starts and completions for each episode.

        Returns an iterator over all episodes.

        Args:
            episode (str): ID of the episode to request data for.
            start (dt.date): Earliest date to request data for.
            end (Optional[dt.date], optional): Most recent date to request data for.
              Defaults to None. Will be set to ``start`` if None.
            page (int): Page number to request
            size (int): Number of results per page
            sort_by (str): Sort by field
            sort_order (str): Sort order
            filter_by (str): Filter by field

        Returns:
            (iterable): [episode]
        """
        if end is None:
            end = start

        url = self._build_url(
            "shows",
            self.podcast_id,
            "episodes",
        )
        date_params = self._date_params(start, end)

        # Yield each episode (handles pagination)
        while True:
            response = self._request(
                url,
                params={
                    **date_params,
                    **{
                        "page": page,
                        "size": size,
                        "sortBy": sort_by,
                        "sortOrder": sort_order,
                        "filter": filter_by,
                    },
                },
            )
            for episode in response["episodes"]:
                yield episode

            if page == response["totalPages"]:
                break

            page += 1

    def catalog(self) -> dict:
        """Loads podcast catalog data.

        Returns:
            dict: [catalog]
        """
        url = self._build_url("user", "shows")

        end = dt.date.today()
        start = end - dt.timedelta(days=30)

        return self._request(
            url,
            params={
                "page": 1,
                "size": 200,
                "sortBy": "name",
                "sortOrder": "ascending",
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d"),
            },
        )

    def performance(
        self,
        episode: str,
    ) -> dict:
        """Gets the episode performance data for a given episode.

        Args:
            episode (str): ID of the episode to request data for.

        Returns:
            dict: [performance]
        """
        url = self._build_url(
            "episodes",
            episode,
            "performance",
        )
        return self._request(url)
