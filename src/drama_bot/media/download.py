"""Bounded HTTPS download with DNS pinning, no redirects/proxies or credential forwarding."""

import hashlib
import http.client
import ipaddress
import os
import socket
import ssl
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit

from drama_bot.contracts import AssetResult


class UnsafeDownload(ValueError):
    pass


class _PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, hostname, address, timeout):
        super().__init__(hostname, port=443, timeout=timeout, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        raw = socket.create_connection((self.address, 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise


class SafeDownloader:
    def __init__(
        self,
        *,
        root: Path,
        allowed_hosts: set[str],
        probe,
        max_bytes: int = 250 * 1024**2,
        timeout: float = 120,
        resolver=socket.getaddrinfo,
        connection_factory=_PinnedHTTPS,
    ):
        self.root = root.resolve()
        self.allowed_hosts = {host.lower() for host in allowed_hosts}
        self.probe = probe
        self.max_bytes = max_bytes
        self.timeout = timeout
        self.resolver = resolver
        self.connection_factory = connection_factory

    def download(self, url: str, destination: Path) -> AssetResult:
        parts = urlsplit(url)
        host = (parts.hostname or "").lower()
        if (
            parts.scheme != "https"
            or host not in self.allowed_hosts
            or parts.port not in (None, 443)
            or parts.username
            or parts.password
            or parts.fragment
        ):
            raise UnsafeDownload("Download URL not permitted")
        addresses = {row[4][0] for row in self.resolver(host, 443, type=socket.SOCK_STREAM)}
        if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
            raise UnsafeDownload("Download DNS contains non-public address")
        destination = destination.resolve()
        if not destination.is_relative_to(self.root) or destination == self.root:
            raise UnsafeDownload("Destination outside asset root")
        if destination.exists():
            raise UnsafeDownload("Original assets cannot be overwritten")
        destination.parent.mkdir(parents=True, exist_ok=True)
        conn = self.connection_factory(host, min(addresses), min(15, self.timeout))
        temp = None
        started = time.monotonic()
        try:
            conn.request(
                "GET",
                parts.path + ("?" + parts.query if parts.query else ""),
                headers={"Accept": "video/*", "Accept-Encoding": "identity"},
            )
            response = conn.getresponse()
            if response.status != 200:
                raise UnsafeDownload("Download must return 200; redirects prohibited")
            length = response.getheader("Content-Length")
            if length is not None and (not length.isdecimal() or int(length) > self.max_bytes):
                raise UnsafeDownload("Download Content-Length exceeds limit")
            digest = hashlib.sha256()
            size = 0
            with tempfile.NamedTemporaryFile(
                dir=destination.parent, suffix=".mp4", delete=False
            ) as f:
                temp = Path(f.name)
                while True:
                    if time.monotonic() - started > self.timeout:
                        raise UnsafeDownload("Download deadline exceeded")
                    chunk = response.read(64 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > self.max_bytes:
                        raise UnsafeDownload("Download exceeds byte limit")
                    digest.update(chunk)
                    f.write(chunk)
                f.flush()
                os.fsync(f.fileno())
            if not size or (length is not None and size != int(length)):
                raise UnsafeDownload("Incomplete download")
            info = self.probe(temp)
            # Hard link is atomic and fails rather than overwriting an existing original.
            os.link(temp, destination)
            return AssetResult(
                path=destination,
                sha256=digest.hexdigest(),
                duration_seconds=info.duration_seconds,
                has_audio=info.has_audio,
                provenance="provider",
            )
        except (OSError, http.client.HTTPException):
            raise UnsafeDownload("Download transport failed") from None
        finally:
            conn.close()
            if temp is not None:
                temp.unlink(missing_ok=True)
