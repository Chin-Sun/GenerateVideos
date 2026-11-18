from types import SimpleNamespace

import pytest

from drama_bot.media.download import SafeDownloader, UnsafeDownload


def resolver(ip):
    return lambda *a, **kw: [(None, None, None, None, (ip, 443))]


def test_ssrf_paths_and_redirects(tmp_path):
    for ip in ("127.0.0.1", "10.0.0.1", "::1", "169.254.169.254"):
        d = SafeDownloader(
            root=tmp_path, allowed_hosts={"cdn.example"}, probe=None, resolver=resolver(ip)
        )
        with pytest.raises(UnsafeDownload):
            d.download("https://cdn.example/a", tmp_path / "a.mp4")
    d = SafeDownloader(
        root=tmp_path, allowed_hosts={"cdn.example"}, probe=None, resolver=resolver("8.8.8.8")
    )
    for url in (
        "http://cdn.example/a",
        "https://evil.example/a",
        "https://u:p@cdn.example/a",
        "https://cdn.example:8443/a",
    ):
        with pytest.raises(UnsafeDownload):
            d.download(url, tmp_path / "a.mp4")
    with pytest.raises(UnsafeDownload):
        d.download("https://cdn.example/a", tmp_path.parent / "escape.mp4")


@pytest.mark.parametrize("status,size,ok", [(200, 3, True), (302, 3, False), (200, 10, False)])
def test_pinned_bounded_download(tmp_path, status, size, ok):
    connections = []

    class Connection:
        def __init__(self, host, address, timeout):
            connections.append((host, address))
            self.sent = False

        def request(self, *args, **kw):
            assert "Authorization" not in kw["headers"]

        def getresponse(self):
            return self

        def getheader(self, name):
            return str(size)

        def read(self, n):
            if self.sent:
                return b""
            self.sent = True
            return b"x" * size

        def close(self):
            pass

    Connection.status = status
    d = SafeDownloader(
        root=tmp_path,
        allowed_hosts={"cdn.example"},
        probe=lambda _: SimpleNamespace(duration_seconds=4, has_audio=True),
        max_bytes=5,
        resolver=resolver("8.8.8.8"),
        connection_factory=Connection,
    )
    if ok:
        asset = d.download("https://cdn.example/a", tmp_path / "a.mp4")
        assert asset.path.read_bytes() == b"xxx"
        assert asset.provenance == "provider"
        with pytest.raises(UnsafeDownload):
            d.download("https://cdn.example/a", tmp_path / "a.mp4")
    else:
        with pytest.raises(UnsafeDownload):
            d.download("https://cdn.example/a", tmp_path / "a.mp4")
        assert not list(tmp_path.iterdir())
    assert connections == [("cdn.example", "8.8.8.8")]
