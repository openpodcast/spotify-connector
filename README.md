# Spotify Connector

This is a simple library for connecting to the inofficial Spotify podcast API.  
It can be used to export data from your dashboard at
https://podcasters.spotify.com/home.

## Supported Data

- List of episodes
- Starts and streams
- Listeners
- Followers
- Gender
- Age
- Country
- Episode performance

## Credentials

Before you can use the library you must extract your Spotify credentials from the dashboard;
they are **not** exposed through your Spotify settings.

You can use our [web-extension](https://github.com/openpodcast/web-extension) for that
or [take a look at the code](https://github.com/openpodcast/web-extension/blob/7ce0865d22bea34fcfc53eec06b25cd076aa8034/src/openpodcast.js)
to see how to do it manually.

## Installation

```
pip install spotifyconnector
```

## Usage as a library

```python
from spotifyconnector import SpotifyConnector

# Set up the connector
connector = SpotifyConnector(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="your_redirect_uri",
    refresh_token="your_refresh_token",
)

# Get podcast metadata
connector.metadata()

# Get the list of listeners of a podcast
listeners = connector.listeners()

# Get the list of followers
followers = connector.aggregate()

# Iterate over all episodes (supports pagination)
for episode in connector.episodes():
    # Do something with episode
    pass

# Get the performance of an episode
performance = connector.performance("episode_id")

# ...
```

See `__main.py__` for all endpoints.

## Development

We use [Pipenv] for virtualenv and dev dependency management. With Pipenv
installed:

1. Install your locally checked out code in [development mode], including its
   dependencies, and all dev dependencies into a virtual environment:

```sh
pipenv sync --dev
```

2. Create an environment file and fill in the required values:

```sh
cp .env.example .env
```

3. Run the script in the virtual environment, which will [automatically load
   your `.env`][env]:

```sh
pipenv run spotifyconnector
```

To add a new dependency for use during the development of this library:

```sh
pipenv install --dev $package
```

To add a new dependency necessary for the correct operation of this library, add
the package to the `install_requires` section of `./setup.py`, then:

```sh
pipenv install
```

To publish the package:

```sh
python setup.py sdist bdist_wheel
twine upload dist/*
```

or

```sh
make publish
```

## Credits

This was inspired by the code at [wdr-okr], extended and released to PyPi.

[pipenv]: https://pipenv.pypa.io/en/latest/index.html#install-pipenv-today
[development mode]: https://setuptools.pypa.io/en/latest/userguide/development_mode.html
[env]: https://pipenv.pypa.io/en/latest/advanced/#automatic-loading-of-env
[wdr-okr]: https://github.com/wdr-data/wdr-okr
