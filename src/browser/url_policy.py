from __future__ import annotations

import ipaddress
import socket
from typing import Iterable, Set
from urllib.parse import urlparse


class URLPolicyError(ValueError):
    pass


class URLPolicy:
    """Reject unsafe network targets unless an official adapter explicitly allows them."""

    def __init__(
        self,
        allow_private_network_targets: bool = False,
        allowed_private_hosts: Iterable[str] = (),
    ):
        self.allow_private_network_targets = allow_private_network_targets
        self.allowed_private_hosts: Set[str] = {
            str(host).rstrip(".").lower() for host in allowed_private_hosts if str(host).strip()
        }

    def validate(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise URLPolicyError("UNSUPPORTED_URL_SCHEME")
        if not parsed.hostname:
            raise URLPolicyError("URL_HOST_REQUIRED")

        host = parsed.hostname.rstrip(".").lower()
        explicitly_allowed = host in self.allowed_private_hosts

        if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
            if not (self.allow_private_network_targets or explicitly_allowed):
                raise URLPolicyError("LOCALHOST_BLOCKED")
            return url

        try:
            literal = ipaddress.ip_address(host)
        except ValueError:
            literal = None

        if literal is not None:
            self._reject_ip(literal, explicitly_allowed)
            return url

        try:
            infos = socket.getaddrinfo(
                host,
                parsed.port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror:
            return url

        for info in infos:
            address = info[4][0]
            try:
                resolved = ipaddress.ip_address(address)
            except ValueError:
                continue
            self._reject_ip(resolved, explicitly_allowed)

        return url

    def _reject_ip(self, ip, explicitly_allowed: bool = False) -> None:
        restricted = (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        )
        if restricted and not (
            self.allow_private_network_targets or explicitly_allowed
        ):
            raise URLPolicyError("NON_PUBLIC_ADDRESS_BLOCKED")
