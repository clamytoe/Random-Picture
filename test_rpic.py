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
