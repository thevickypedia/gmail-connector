import socket
from typing import Any, List


def hostname_to_ip(hostname: str) -> List[str]:
    """Uses ``socket.gethostbyname_ex`` to translate a host name to IPv4 address format, extended interface.

    References:
        https://docs.python.org/3/library/socket.html#socket.gethostbyname_ex

    Args:
        hostname: Takes the hostname of a device as an argument.
    """
    try:
        _hostname, _alias_list, _ipaddr_list = socket.gethostbyname_ex(hostname)
    except socket.error:
        return []
    return _ipaddr_list


def matrix_to_flat_list(input_: List[list]) -> list:
    """Converts a matrix into flat list.

    Args:
        input_: Takes a list of list as an argument.

    Returns:
        list:
        Flat list.
    """
    return sum(input_, []) or [item for sublist in input_ for item in sublist]


def remove_duplicates(input_: List[Any]) -> List[Any]:
    """Remove duplicate values from a list.

    Args:
        input_: Takes a list as an argument.

    Returns:
        list:
        Returns a cleaned up list.
    """
    # return list(set(input_))
    return [i.strip() for n, i in enumerate(input_) if i not in input_[n + 1:]]
