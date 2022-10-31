import re
import smtplib
import socket
from typing import Union

from gmailconnector.responder import Response

from .address import ValidateAddress
from .domain import get_mx_records
from .exceptions import AddressFormatError, InvalidDomain, NotMailServer
from .port import is_port_allowed


def validate_email(email_address: str, smtp_timeout: Union[int, float] = 5, sender: str = None) -> Response:
    """Validates email address deliver-ability using SMTP.

    Args:
        email_address: Email address.
        smtp_timeout: Time in seconds to wait for a result.
        sender: Sender's email address.

    Warnings:
        - This is not a perfect solution for validating email address.
        - Works perfect for gmail, but yahoo and related mail servers always returns OK even with garbage email address.
        - Works only if port 25 is not blocked by ISP.
        - SMTP Timeout ``(smtp_timeout)`` specified is to create a socket connection with each mail exchange server.
        - If a mail server has 10 mx records and timeout is set to 3, the total wait time will be 30 seconds.

    See Also:
        - Sets the ``ok`` flag in Response class to
            - ``False`` only if the email address or domain is clearly invalid.
            - ``True`` only if the email address is clearly valid.
            - ``None`` if port 25 is blocked or all mx records returned temporary errors.

    Returns:
        bool:
        Boolean flag to indicate if the email address is valid.
    """
    try:
        address = ValidateAddress(address=email_address)
    except AddressFormatError as error:
        return Response(dictionary={
            'ok': False,
            'status': 422,
            'body': f"Invalid address: {email_address!r}. {error}" if str(error).strip() else
            f"Invalid address: {email_address!r}."
        })

    try:
        mx_records = get_mx_records(domain=address.domain)
    except InvalidDomain as error:
        return Response(dictionary={
            'ok': False,
            'status': 422,
            'body': error.__str__()
        })
    except NotMailServer as error:
        return Response(dictionary={
            'ok': False,
            'status': 422,
            'body': error.__str__()
        })

    if not is_port_allowed():
        return Response(dictionary={
            'ok': None,
            'status': 305,
            'body': 'Cannot verify SMTP since port 25 has been blocked.'
        })

    server = smtplib.SMTP(timeout=smtp_timeout)
    for record in mx_records:
        try:
            server.connect(host=record)
        except socket.error:
            continue
        server.ehlo_or_helo_if_needed()
        server.mail(sender=sender)
        code, msg = server.rcpt(recip=address.email)
        msg = re.sub(r"\d+.\d+.\d+", '', msg.decode(encoding='utf-8')).strip()
        msg = ' '.join(msg.splitlines()).replace('  ', ' ').strip() if msg else "Unknown error"
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
