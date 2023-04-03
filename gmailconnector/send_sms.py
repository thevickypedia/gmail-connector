import os
import smtplib
import socket
from typing import NoReturn, Union

from .models.config import Encryption, SMSGateway
from .models.responder import Response
from .sms_deleter import DeleteSent


class SendSMS:
    """Initiates Messenger object to send an SMS to a phone number using SMS gateway provided by the mobile carrier.

    >>> SendSMS

    """

    def __init__(self, gmail_user: str = None, gmail_pass: str = None, timeout: Union[int, float] = 10,
                 gmail_host: str = "smtp.gmail.com", encryption: Encryption.__str__ = Encryption.TLS):
        """Initiates all the necessary args.

        Args:
            gmail_user: Gmail username to authenticate SMTP lib.
            gmail_pass: Gmail password to authenticate SMTP lib.
            timeout: Connection timeout for SMTP lib.
            encryption: Type of encryption to be used.
            gmail_host: Hostname for gmail's smtp server.
        """
        gmail_user = gmail_user or os.environ.get('gmail_user') or os.environ.get('GMAIL_USER')
        gmail_pass = gmail_pass or os.environ.get('gmail_pass') or os.environ.get('GMAIL_PASS')
        self.server, self.error = None, None
        if not all([gmail_user, gmail_pass]):
            raise ValueError("'gmail_user' and 'gmail_pass' are mandatory")
        if encryption not in (Encryption.TLS, Encryption.SSL):
            raise ValueError(
                'Encryption should either be TLS or SSL'
            )
        if gmail_user.endswith('@gmail.com'):
            self.gmail_user = gmail_user
        else:
            self.gmail_user = gmail_user + '@gmail.com'
        self.gmail_pass = gmail_pass
        self._authenticated = False
        if encryption == Encryption.TLS:
            self.create_tls_connection(host=gmail_host, timeout=timeout)
        else:
            self.create_ssl_connection(host=gmail_host, timeout=timeout)

    def create_ssl_connection(self, host: str, timeout: Union[int, float]) -> NoReturn:
        """Create a connection using SSL encryption."""
        try:
            self.server = smtplib.SMTP_SSL(host=host, port=465, timeout=timeout)
        except (smtplib.SMTPException, socket.error) as error:
            self.error = error.__str__()

    def create_tls_connection(self, host: str, timeout: Union[int, float]) -> NoReturn:
        """Create a connection using TLS encryption."""
        try:
            self.server = smtplib.SMTP(host=host, port=587, timeout=timeout)
            self.server.starttls()
        except (smtplib.SMTPException, socket.error) as error:
            self.error = error.__str__()

    @property
    def authenticate(self) -> Response:
        """Initiates authentication.

        Returns:
            Response:
            A custom response class with properties: ok, status and body to the user.
        """
        if self.server is None:
            return Response(dictionary={
                'ok': False,
                'status': 408,
                'body': self.error or "failed to create a connection with gmail's SMTP server"
            })
        try:
            self.server.login(user=self.gmail_user, password=self.gmail_pass)
            self._authenticated = True
            return Response(dictionary={
                'ok': True,
                'status': 200,
                'body': 'authentication success'
            })
        except smtplib.SMTPAuthenticationError:
            return Response(dictionary={
                'ok': False,
                'status': 401,
                'body': 'authentication failed'
            })
        except smtplib.SMTPException as error:
            return Response(dictionary={
                'ok': False,
                'status': 503,
                'body': error.__str__()
            })

    def __del__(self):
        """Destructor has been called to close the connection and logout."""
        if self.server:
            self.server.close()

    @staticmethod
    def validate_phone(phone: str) -> NoReturn:
        """Validates all the arguments passed during object initialization.

        Args:
            phone: Phone number.
        """
        if len(phone) != 10 and len(phone) != 12:
            raise ValueError('Phone number should either be 10 or 12 digits (if includes country code)')
        if phone.startswith('+') and not phone.startswith('+1'):
            raise ValueError('Unsupported country code. Module works only for US based contact numbers.')

    @staticmethod
    def generate_address(phone: str, gateway: str) -> str:
        """Validates the digits in the phone number and forms the endpoint using the phone number and sms gateway.

        Returns:
            str:
            Returns the formed endpoint. `Example: ``+11234567890@tmomail.net```
        """
        if len(phone) == 11 and phone.startswith('1'):
            phone = f'+{phone}'
        if not phone.startswith('+'):
            phone = f'+1{phone}'
        return phone + '@' + gateway

    def send_sms(self, message: str, phone: str = None, subject: str = None,
                 sms_gateway: SMSGateway.__str__ = SMSGateway.tmobile,
                 delete_sent: bool = False) -> Response:
        """Initiates a TLS connection and sends a text message through SMS gateway of destination number.

        Args:
            phone: Phone number.
            message: Content of the message.
            subject: Subject line for the message. Defaults to "Message from GmailConnector"
            sms_gateway: Takes the SMS gateway of the carrier as an argument.
            delete_sent: Boolean flag to delete the message from GMAIL's sent items. Defaults to ``False``.

        See Also:
            - Encodes body of the message to `ascii` with `ignore` flag and then decodes it.
            - This is done to ignore special characters (like °) without raising `UnicodeEncodeError`
            - Validates the endpoint ``phone-number@sms-gateway`` before trying to send the SMS.

        Notes:
            Other flags that can be set includes `replace` and `xmlcharrefreplace`

        Returns:
            Response:
            A custom response class with properties: ok, status and body to the user.
        """
        phone = phone or os.environ.get('phone') or os.environ.get('PHONE')
        if phone:
            phone = str(phone)
        else:
            raise ValueError(
                'Cannot proceed without the arg: `phone`'
            )

        self.validate_phone(phone=phone)
        body = f'\n\n{message}'.encode('ascii', 'ignore').decode('ascii')
        subject = subject or f"Message from {self.gmail_user.replace('@gmail.com', '')}"
        if sms_gateway not in SMSGateway.all:
            raise ValueError(
                f"SMS gateway should be any one of {', '.join(SMSGateway.all)!r}"
            )
        to = self.generate_address(phone=phone, gateway=sms_gateway)
        if not self._authenticated:
            status = self.authenticate
            if not status.ok:
                return status
        message = (f"From: {self.gmail_user}\n" + f"To: {to}\n" + f"Subject: {subject}\n" + body)
        if len(message) > 428:
            return Response(dictionary={
                'ok': False,
                'status': 413,
                'body': f'Payload length: {len(message):,}, which is more than the optimal size: 428. '
                        f'Message length: {len(body):,}'
            })

        self.server.sendmail(
            from_addr=self.gmail_user,
            to_addrs=to,
            msg=message
        )

        if delete_sent:
            if delete_response := DeleteSent(username=self.gmail_user, password=self.gmail_pass,
                                             subject=subject, body=body, to=to).delete_sent():
                return Response(dictionary={
                    'ok': True,
                    'status': 200,
                    'body': f'SMS has been sent to {to}',
                    'extra': delete_response
                })
            else:
                return Response(dictionary={
                    'ok': True,
                    'status': 206,
                    'body': f'SMS has been sent to {to}',
                    'extra': 'Failed to locate and delete the SMS from Sent Mail.'
                })

        return Response(dictionary={
            'ok': True,
            'status': 200,
            'body': f'SMS has been sent to {to}'
        })
