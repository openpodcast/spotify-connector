# Spotify Connector

This is a simple library for connecting to the inofficial Spotify podcast API.
It can be used to export data from the dashboard.

## Supported Data

- List of episodes
- Starts and streams
- Listeners
- Followers
- Gender
- Age
- Country
- Episode performance

## Usage as a library

```python
from spotify_importer import SpotifyImporter

connector = SpotifyConnector(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="your_redirect_uri",
    refresh_token="your_refresh_token",
)

# Get the list of episodes
episodes = connector.get_episodes()

# Get the list of listeners
listeners = connector.get_listeners()

# Get the list of followers
followers = connector.get_followers()

# ...
```

## Usage As An Application

1. Create an environment file and fill in the required values:

```sh
cp .env.example .env
```

2. Run the script:

```sh
python3 main.py
```
