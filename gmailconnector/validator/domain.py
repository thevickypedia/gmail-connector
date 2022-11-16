import logging
import socket
from ipaddress import IPv4Address, IPv6Address
from typing import Iterable, Union

from dns.rdtypes.ANY.MX import MX
from dns.resolver import NXDOMAIN, Answer, NoAnswer, resolve

from .exceptions import InvalidDomain, NotMailServer

logger = logging.getLogger('validator')


def get_mx_records(domain: str) -> Iterable[Union[str, IPv4Address, IPv6Address]]:
    """Get MX (Mail Exchange server) records for the given domain.

    Args:
        domain: FQDN (Fully Qualified Domain Name) extracted from the email address.

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
    for x in resolved:
        x: MX = x
        ip = socket.gethostbyname(x.exchange.to_text())
        logger.info(f"{x.preference}\t{x.exchange}\t{ip}")
        yield ip
