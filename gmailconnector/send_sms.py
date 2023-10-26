import smtplib
import socket
from typing import Union

from typing_extensions import Unpack

from .models.config import EgressConfig, Encryption, SMSGateway
from .models.responder import Response
from .sms_deleter import DeleteSent


class SendSMS:
    """Initiates Messenger object to send an SMS to a phone number using SMS gateway provided by the mobile carrier.

    >>> SendSMS

    """

    def __init__(self, **kwargs: 'Unpack[EgressConfig]'):
        """Initiates necessary args, creates a connection with Gmail host based on chosen encryption type.

        Keyword Args:
            gmail_user: Gmail username to authenticate SMTP lib.
            gmail_pass: Gmail password to authenticate SMTP lib.
            timeout: Connection timeout for SMTP lib.
            encryption: Type of encryption to be used.
            gmail_host: Hostname for gmail's smtp server.
        """
        self.server, self.error = None, None
        self.env = EgressConfig(**kwargs)
        self._authenticated = False
        if self.env.encryption == Encryption.TLS:
            self.create_tls_connection(host=self.env.gmail_host, timeout=self.env.timeout)
        else:
            self.create_ssl_connection(host=self.env.gmail_host, timeout=self.env.timeout)

    def create_ssl_connection(self, host: str, timeout: Union[int, float]) -> None:
        """Create a connection using SSL encryption."""
        try:
            self.server = smtplib.SMTP_SSL(host=host, port=465, timeout=timeout)
        except (smtplib.SMTPException, socket.error) as error:
            self.error = error.__str__()

    def create_tls_connection(self, host: str, timeout: Union[int, float]) -> None:
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
            self.server.login(user=self.env.gmail_user, password=self.env.gmail_pass)
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
    def generate_address(phone: str, gateway: str) -> str:
        """Validates the digits in the phone number and forms the endpoint using the phone number and sms gateway.

        Returns:
            str:
            Returns the formed endpoint. `Example: ``+11234567890@tmomail.net```
        """
        phone = f'+1{phone}'
        return phone + '@' + gateway

    def send_sms(self, message: str, phone: str = None, subject: str = None,
                 sms_gateway: SMSGateway = None,
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
        phone = phone or self.env.phone
        if not phone:
            raise ValueError(
                '\n\tCannot proceed without phone number'
            )

        body = f'\n\n{message}'.encode('ascii', 'ignore').decode('ascii')
        subject = subject or f"Message from {self.env.gmail_user.replace('@gmail.com', '')}"
        if not sms_gateway:
            sms_gateway = SMSGateway.tmobile
        elif sms_gateway not in SMSGateway.all:
            raise ValueError(
                f"SMS gateway should be one of {', '.join(SMSGateway.all)!r}"
            )
        to = self.generate_address(phone=phone, gateway=sms_gateway)
        if not self._authenticated:
            status = self.authenticate
            if not status.ok:
                return status
        message = (f"From: {self.env.gmail_user}\n" + f"To: {to}\n" + f"Subject: {subject}\n" + body)
        if len(message) > 428:
            return Response(dictionary={
                'ok': False,
                'status': 413,
                'body': f'Payload length: {len(message):,}, which is more than the optimal size: 428. '
                        f'Message length: {len(body):,}'
            })

        self.server.sendmail(
            from_addr=self.env.gmail_user,
            to_addrs=to,
            msg=message
        )

        if delete_sent:
            if delete_response := DeleteSent(username=self.env.gmail_user, password=self.env.gmail_pass,
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
