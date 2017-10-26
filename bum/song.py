"""
Get song info.
"""
import shutil
import os
import mpd

from . import brainz
from . import util


def init(port=6600):
    """Initialize mpd."""
    client = mpd.MPDClient()

    try:
        client.connect("localhost", port)
        return client

    except ConnectionRefusedError:
        print("error: Connection refused to mpd/mopidy.")
        os._exit(1)  # pylint: disable=W0212


def get_art(cache_dir, size, client):
    """Get the album art."""
    song = client.currentsong()

    if len(song) < 2:
        print("album: Nothing currently playing.")
        return

    file_name = f"{song['artist']}_{song['album']}_{size}.jpg".replace("/", "")
    file_name = cache_dir / file_name

    if file_name.is_file():
        shutil.copy(file_name, cache_dir / "current.jpg")
        print("album: Found cached art.")

    else:
        print("album: Downloading album art...")

        brainz.init()
        album_art = brainz.get_cover(song, size)

        if album_art:
            util.bytes_to_file(album_art, cache_dir / file_name)
            util.bytes_to_file(album_art, cache_dir / "current.jpg")

            print(f"album: Swapped art to {song['artist']}, {song['album']}.")

        """
        If no album art found:
        Look for a file with the same name as the artist in cache_dir/fallback
        Read file, write it to current.jpg
        TODO: Make it more flexible. Right now file name has to be exactly {artist name}.jpg (slashes removed)
        TODO: Check if file exists before reading it!
        """
        if not album_art:
            file_name = f"{song['artist']}.jpg".replace("/", "")
            file_name = cache_dir / 'fallback' / file_name
            album_art = util.file_to_bytes(file_name)
            util.bytes_to_file(album_art, cache_dir / "current.jpg")

            print(f"album: Swapped art to fallback image for {song['artist']}.")

