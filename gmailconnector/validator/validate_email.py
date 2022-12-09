import logging
import re
import smtplib
import socket
from typing import Union

from gmailconnector.responder import Response

from .address import ValidateAddress
from .domain import get_mx_records
from .exceptions import AddressFormatError, InvalidDomain, NotMailServer

formatter = logging.Formatter(fmt='%(levelname)s\t %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(fmt=formatter)

logger = logging.getLogger('validator')
logger.addHandler(hdlr=handler)
logger.setLevel(level=logging.DEBUG)


def validate_email(email_address: str, timeout: Union[int, float] = 5, sender: str = None,
                   debug: bool = False, smtp_check: bool = True) -> Response:
    """Validates email address deliver-ability using SMTP.

    Args:
        email_address: Email address.
        timeout: Time in seconds to wait for a result.
        sender: Sender's email address.
        debug: Debug flag enable logging.
        smtp_check: Flag to check SMTP.

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
        address = ValidateAddress(address=email_address)
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
        except (InvalidDomain, NotMailServer) as error:
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

    server = smtplib.SMTP(timeout=timeout)
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
    except (InvalidDomain, NotMailServer) as error:
        logger.error(error)
        return Response(dictionary={
            'ok': False,
            'status': 422,
            'body': error.__str__()
        })
