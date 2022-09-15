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

# Get podcast metadata
connector.metadata()

# Get the list of episodes
episodes = connector.episodes()

# Get the list of listeners
listeners = connector.listeners()

# Get the list of followers
followers = connector.aggregate()

# ...
```

## Development

1. Create a virtual environment:

```sh
python3 -m venv venv
```

2. Activate the virtual environment:

```sh
source venv/bin/activate
```

3. Install the dependencies:

```sh
pip install -r requirements.txt
```

4. Create an environment file and fill in the required values:

```sh
cp .env.example .env
```

5. Run the script:

```sh
python3 -m spotifyconnector
```

6. Publish the package:

```sh
python3 setup.py sdist bdist_wheel
twine upload dist/*
```
