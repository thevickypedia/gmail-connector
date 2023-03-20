import logging
import socket
from collections.abc import Generator
from ipaddress import IPv4Address, IPv6Address
from typing import Iterable, Union

from dns.rdtypes.ANY.MX import MX
from dns.resolver import NXDOMAIN, Answer, NoAnswer, resolve

from .exceptions import InvalidDomain, NotMailServer, UnresponsiveMailServer

default_logger = logging.getLogger('validator')


def get_mx_records(domain: str,
                   logger: logging.Logger = default_logger) -> Generator[Union[str, IPv4Address, IPv6Address]]:
    """Get MX (Mail Exchange server) records for the given domain.

    Args:
        domain: FQDN (Fully Qualified Domain Name) extracted from the email address.
        logger: Bring your own logger.

    Yields:
        IPv4Address:
        IP addresses of the mail exchange servers from authoritative/non-authoritative answer section.
    """
    try:
        resolved: Iterable[Answer] = resolve(domain, 'MX')
    except NXDOMAIN as error:
        raise InvalidDomain(error)
    except NoAnswer as error:
        raise NotMailServer(error)
    if not resolved:
        raise NotMailServer(f"Domain {domain!r} is not a mail server.")
    for record in resolved:
        record: MX = record
        if record.exchange.to_text().strip() == '.':
            raise UnresponsiveMailServer(f"Domain {domain!r} appears to be valid, but failed to resolve IP addresses.")
        try:
            ip = socket.gethostbyname(record.exchange.to_text())
        except socket.error as error:
            logger.error(error)
            raise UnresponsiveMailServer(error)
        except UnicodeError as error:
            logger.error(error)
            raise UnresponsiveMailServer(f"Domain {domain!r} appears to be valid, but failed to resolve IP addresses.")
        logger.info(f"{record.preference}\t{record.exchange}\t{ip}")
        yield ip
