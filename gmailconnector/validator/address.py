import logging
from ipaddress import IPv4Address, IPv6Address
from typing import Union

import idna.core

from .exceptions import AddressFormatError

default_logger = logging.getLogger('validator')


class EmailAddress:
    """Initiates ValidateAddress object to split the address into user and domin to further validate.

    >>> EmailAddress

    """

    def __init__(self, address: str, logger: logging.Logger = default_logger):
        self._address = address
        try:
            self._user, self._domain = self._address.rsplit('@', 1)
        except ValueError:
            raise AddressFormatError
        if not self._user:
            raise AddressFormatError("Empty user")
        try:
            self._domain = idna.core.encode(self._domain).decode('ascii')
        except idna.core.IDNAError as error:
            raise AddressFormatError(error)
        logger.info(f'Validation passed on {address}')

    @property
    def user(self) -> str:
        """Returns only the user part of the address."""
        return self._user

    @property
    def domain(self) -> Union[str, IPv4Address, IPv6Address]:
        """Returns only the domain part of the address."""
        return self._domain

    @property
    def email(self) -> str:
        """Returns the email address."""
        return '@'.join((self.user, self.domain))
