from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class URLPolicyError(ValueError):
    pass


class URLPolicy:
    """Basic SSRF guard for live retrieval.

    Only http/https URLs are accepted. Literal and resolved private, loopback,
    link-local, multicast and reserved addresses are rejected.
    """

    def validate(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise URLPolicyError("UNSUPPORTED_URL_SCHEME")
        if not parsed.hostname:
            raise URLPolicyError("URL_HOST_REQUIRED")
        host = parsed.hostname.rstrip(".").lower()
        if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
            raise URLPolicyError("LOCALHOST_BLOCKED")

        try:
            literal = ipaddress.ip_address(host)
            self._reject_ip(literal)
            return url
        except ValueError:
            pass

        try:
            infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
        except socket.gaierror:
            # DNS failure is a retrieval error, not proof that the URL is unsafe.
            return url

        for info in infos:
            address = info[4][0]
            try:
                self._reject_ip(ipaddress.ip_address(address))
            except ValueError:
                continue
        return url

    def _reject_ip(self, ip: ipaddress._BaseAddress) -> None:
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise URLPolicyError("NON_PUBLIC_ADDRESS_BLOCKED")
