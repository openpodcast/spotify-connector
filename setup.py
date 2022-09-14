from setuptools import find_packages, setup

setup(
    name='spotifyconnector',
    packages=find_packages(include=['spotifyconnector']),
    version='0.1.0',
    description='Spotify Connector for Podcast Data',
    author='Open Podcast',
    license='MIT',
    install_requires=[
        'requests',
        'loguru',
        'PyYAML',
        'tenacity'
    ],
)