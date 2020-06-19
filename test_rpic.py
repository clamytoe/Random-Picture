from os import path, rmdir
import pytest

from rpic import Wallhaven


@pytest.fixture(scope="session")
def haven():
    return Wallhaven()


def test_url(haven):
    url = (
        "https://wallhaven.cc/search?categories=111&purity=100&"
        "atleast=1920x1080&sorting=random&order=desc"
    )
    assert haven.url == url


def test_local_path(haven):
    assert haven.local_path == "/home/mohh/Pictures/wallpaper.jpg"


def test_wallpapers(haven):
    assert haven.wallpapers == "/home/mohh/Pictures/wallpapers"


def test_check_dir(haven):
    tmp = "tmp"
    assert not path.exists(tmp)
    haven.check_dir(tmp)
    assert path.exists(tmp)
    assert path.isdir(tmp)
    rmdir(tmp)
