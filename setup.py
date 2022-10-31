from setuptools import find_packages, setup

setup(
    name='spotifyconnector',
    packages=find_packages(include=['spotifyconnector']),
    version='0.4.0',
    description='Spotify Connector for Podcast Data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Open Podcast',
    license='MIT',
    entry_points={
        'console_scripts': [
            'spotifyconnector = spotifyconnector.__main__:main',
        ]
    },
    install_requires=[
        'requests',
        'loguru',
        'PyYAML',
        'tenacity'
    ],
)
