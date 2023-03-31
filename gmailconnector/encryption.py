from enum import Enum


class Encryption(str, Enum):
    """Enum wrapper for TLS and SSL encryption."""

    TLS: str = "TLS"
    SSL: str = "SSL"
