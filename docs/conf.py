# pylint: skip-file

project = "spotify-connector"
copyright = "2024, OpenPodcast"
author = "OpenPodcast"

version = "0.8.2"
release = "0.8.2"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "myst_parser",  # enable markdown
]

templates_path = ["_templates"]

source_suffix = [".rst", ".md"]

master_doc = "index"

exclude_patterns = ["dist", "build", "_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
