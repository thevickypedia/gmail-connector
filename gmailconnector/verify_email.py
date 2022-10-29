import contextlib
import os
import re
import smtplib
import socket
import subprocess
from typing import Any, List, Union

from .responder import Response


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


def get_mx_records(domain: str) -> List:
    """Get MX (Mail Exchange server) records for the given domain.

    Args:
        domain: FQDN (Fully Qualified Domain Name) extracted from the email address.

    Returns:
        list:
        List of IP addresses of all the mail exchange servers from authoritative/non-authoritative answer section.
    """
    try:
        output = subprocess.check_output(f'nslookup -q=mx {domain}', shell=True)
        result = [hostname_to_ip(hostname=line.split()[-1]) for line in output.decode().splitlines()
                  if line.startswith(domain)]
        return remove_duplicates(input_=matrix_to_flat_list(input_=result))
    except subprocess.CalledProcessError:
        return []


def is_port_allowed(host: str = 'gmail.com', port: int = smtplib.SMTP_PORT):
    """Replicates ``telnet`` command by trying to create a socket connection on a particular host and port.

    Args:
        host: Host that has to be tried. Defaults to 'gmail.com'
        port: Port number that has to be checked. Defaults to SMTP port 25.

    Returns:
        bool:
        Boolean flag to indicate whether the port is allowed.
    """
    with contextlib.closing(thing=socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True


def validate(email: str, timeout: Union[int, float] = 5) -> Response:
    """Validates email address deliver-ability using SMTP.

    Args:
        email: Email address.
        timeout: Time in seconds to wait for a result.

    Warnings:
        - Timeout specified is to create a socket connection with each mail exchange server.
        - If a mail server has 10 mx records and timeout is set to 3, the total wait time will be 30 seconds.

    Warnings:
        - This is not a perfect solution for validating email address.
        - Works perfect for gmail, but yahoo and related mail servers always returns OK even with garbage email address.
        - Works only if port 25 is not blocked by ISP.

    See Also:
        - Sets the ``ok`` flag in Response class to
            - ``False`` only if the email address or domain is clearly invalid.
            - ``True`` only if the email address is clearly valid.
            - ``None`` if port 25 is blocked or all mx records returned temporary errors.

    Returns:
        bool:
        Boolean flag to indicate if the email address is valid.
    """
    if not (mx_records := get_mx_records(domain=email.split('@')[-1])):
        return Response(dictionary={
            'ok': False,
            'status': 422,
            'body': f"Invalid domain {email.split('@')[-1]!r}."
        })

    if not is_port_allowed():
        return Response(dictionary={
            'ok': None,
            'status': 305,
            'body': 'Cannot verify SMTP since port 25 has been blocked.'
        })

    server = smtplib.SMTP(timeout=timeout)
    for record in mx_records:
        try:
            server.connect(host=record)
        except socket.error:
            continue
        server.ehlo_or_helo_if_needed()
        server.mail(sender=os.environ.get('GMAIL_USER'))
        code, msg = server.rcpt(recip=email)
        msg = re.sub(r"\d+.\d+.\d+", '', msg.decode(encoding='utf-8')).strip()
        if msg:
            msg = ' '.join(msg.splitlines()).replace('  ', ' ').strip()
        if code == 550:  # Definitely invalid email address
            return Response({
                'ok': False,
                'status': 550,
                'body': msg
            })
        if code < 400:  # Valid email address
            return Response({
                'ok': True,
                'status': 200,
                'body': msg
            })
    return Response({
        'ok': None,
        'status': 207,
        'body': 'Received multiple temporary errors. Could not finish validation.'
    })
