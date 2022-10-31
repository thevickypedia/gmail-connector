class AddressFormatError(ValueError):
    """Custom error object for invalid address format."""


class NotMailServer(ValueError):
    """Custom error object for domain that is not a mail server."""


class InvalidDomain(ValueError):
    """Custom error object for invalid domain."""
