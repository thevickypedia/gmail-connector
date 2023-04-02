import logging
import re
import smtplib
import socket
from typing import Union

from ..models.responder import Response
from .address import EmailAddress
from .domain import get_mx_records
from .exceptions import (AddressFormatError, InvalidDomain, NotMailServer,
                         UnresponsiveMailServer)

formatter = logging.Formatter(fmt='%(levelname)s\t %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(fmt=formatter)

default_logger = logging.getLogger('validator')
default_logger.addHandler(hdlr=handler)
default_logger.setLevel(level=logging.DEBUG)


def validate_email(email_address: str, timeout: Union[int, float] = 5, sender: str = None,
                   debug: bool = False, smtp_check: bool = True, logger: logging.Logger = default_logger) -> Response:
    """Validates email address deliver-ability using SMTP.

    Args:
        email_address: Email address.
        timeout: Time in seconds to wait for a result.
        sender: Sender's email address.
        debug: Debug flag enable logging.
        smtp_check: Flag to check SMTP.
        logger: Bring your own logger.

    See Also:
        - Sets the ``ok`` flag in Response class to
            - ``False`` only if the email address or domain is clearly invalid.
            - ``True`` only if the email address is clearly valid.
            - ``None`` if port 25 is blocked or all mx records returned temporary errors.

    Returns:
        bool:
        Boolean flag to indicate if the email address is valid.
    """
    if debug is False:
        logger.disabled = True
    try:
        address = EmailAddress(address=email_address)
    except AddressFormatError as error:
        return Response(dictionary={
            'ok': False,
            'status': 422,
            'body': f"Invalid address: {email_address!r}. {error}" if str(error).strip() else
            f"Invalid address: {email_address!r}."
        })

    if not smtp_check:
        try:
            list(get_mx_records(domain=address.domain))
        except (InvalidDomain, NotMailServer, UnresponsiveMailServer) as error:
            logger.error(error)
            return Response(dictionary={
                'ok': False,
                'status': 422,
                'body': error.__str__()
            })
        return Response(dictionary={
            'ok': True,
            'status': 200,
            'body': f'{address.email!r} is valid'
        })

    try:
        server = smtplib.SMTP(timeout=timeout)
    except (smtplib.SMTPException, socket.error) as error:
        return Response(dictionary={
            'ok': False,
            'status': 408,
            'body': error.__str__() or "failed to create a connection with gmail's SMTP server"
        })
    try:
        for record in get_mx_records(domain=address.domain):
            logger.info(f'Trying {record}...')
            try:
                server.connect(host=record)
            except socket.error as error:
                logger.error(error)
                continue
            server.ehlo_or_helo_if_needed()
            server.mail(sender=sender or address.email)
            code, msg = server.rcpt(recip=address.email)
            msg = re.sub(r"\d+.\d+.\d+", '', msg.decode(encoding='utf-8')).strip()
            msg = ' '.join(msg.splitlines()).replace('  ', ' ').strip() if msg else "Unknown error"
            if code == 550:  # Definitely invalid email address
                logger.info(f'Invalid email address: {address.email}')
                return Response(dictionary={
                    'ok': False,
                    'status': 550,
                    'body': msg
                })
            if code < 400:  # Valid email address
                logger.info(f'Valid email address: {address.email}')
                return Response(dictionary={
                    'ok': True,
                    'status': 200,
                    'body': f"'{msg}' at MX:{record}"
                })
            logger.info(f'Temporary error: {code} - {msg}')
        logger.error('Received multiple temporary errors. Could not finish validation.')
        return Response(dictionary={
            'ok': None,
            'status': 207,
            'body': 'Received multiple temporary errors. Could not finish validation.'
        })
    except (InvalidDomain, NotMailServer, UnresponsiveMailServer) as error:
        logger.error(error)
        return Response(dictionary={
            'ok': False,
            'status': 422,
            'body': error.__str__()
        })
