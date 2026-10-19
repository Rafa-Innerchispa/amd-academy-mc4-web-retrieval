from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class URLPolicyError(ValueError):
    pass


class URLPolicy:
    """Reject non-public retrieval targets before any network request."""

    def validate(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise URLPolicyError("UNSUPPORTED_URL_SCHEME")
        if not parsed.hostname:
            raise URLPolicyError("URL_HOST_REQUIRED")

        host = parsed.hostname.rstrip(".").lower()
        if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
            raise URLPolicyError("LOCALHOST_BLOCKED")

        # Parse literal IPs without accidentally swallowing our own policy error.
        try:
            literal = ipaddress.ip_address(host)
        except ValueError:
            literal = None

        if literal is not None:
            self._reject_ip(literal)
            return url

        try:
            infos = socket.getaddrinfo(
                host,
                parsed.port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror:
            # DNS failure is handled by the fetch layer. It is not itself a
            # reason to classify the URL as a private target.
            return url

        for info in infos:
            address = info[4][0]
            try:
                resolved = ipaddress.ip_address(address)
            except ValueError:
                continue
            self._reject_ip(resolved)

        return url

    def _reject_ip(self, ip) -> None:
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise URLPolicyError("NON_PUBLIC_ADDRESS_BLOCKED")
