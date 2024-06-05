import re
import smtplib
import socket
from typing import Union

from typing_extensions import Unpack

from .models.config import EgressConfig, Encryption, SMSGateway
from .models.responder import Response
from .sms_deleter import DeleteSent

COUNTRY_CODE = re.compile("^\\+\\d+")


class SendSMS:
    """Initiates Messenger object to send an SMS to a phone number using SMS gateway provided by the mobile carrier.

    >>> SendSMS

    """

    def __init__(self, **kwargs: "Unpack[EgressConfig]"):
        """Loads all the necessary args, creates a connection with Gmail host based on chosen encryption type.

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
            self.create_tls_connection(
                host=self.env.gmail_host, timeout=self.env.timeout
            )
        else:
            self.create_ssl_connection(
                host=self.env.gmail_host, timeout=self.env.timeout
            )

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
            A custom response object with properties: ok, status and body to the user.
        """
        if self.server is None:
            return Response(
                dictionary={
                    "ok": False,
                    "status": 408,
                    "body": self.error
                    or "failed to create a connection with gmail's SMTP server",
                }
            )
        try:
            self.server.login(user=self.env.gmail_user, password=self.env.gmail_pass)
            self._authenticated = True
            return Response(
                dictionary={"ok": True, "status": 200, "body": "authentication success"}
            )
        except smtplib.SMTPAuthenticationError:
            return Response(
                dictionary={"ok": False, "status": 401, "body": "authentication failed"}
            )
        except smtplib.SMTPException as error:
            return Response(
                dictionary={"ok": False, "status": 503, "body": error.__str__()}
            )

    def __del__(self):
        """Destructor has been called to close the connection and logout."""
        if self.server:
            self.server.close()

    def send_sms(
        self,
        message: str,
        phone: str = None,
        country_code: str = None,
        subject: str = None,
        sms_gateway: SMSGateway = None,
        delete_sent: bool = False,
    ) -> Response:
        """Initiates an SMTP connection and sends a text message through SMS gateway of destination number.

        Args:
            phone: Phone number.
            message: Content of the message.
            country_code: Country code of the phone number.
            subject: Subject line for the message. Defaults to "Message from email address."
            sms_gateway: Takes the SMS gateway of the carrier as an argument.
            delete_sent: Boolean flag to delete the message from GMAIL's sent items. Defaults to ``False``.

        See Also:
            - Encodes body of the message to `ascii` with `ignore` flag and then decodes it.
            - This is done to ignore special characters (like °) without raising `UnicodeEncodeError`

        Notes:
            Other flags that can be set includes `replace` and `xmlcharrefreplace`

        Returns:
            Response:
            A custom response object with properties: ok, status and body to the user.
        """
        if not all((phone, len(phone) == 10)):
            raise ValueError("\n\tcannot proceed without a valid phone number")
        if not sms_gateway:
            sms_gateway = SMSGateway.tmobile
        if not country_code:
            country_code = "+1"
        if COUNTRY_CODE.match(country_code):
            to = country_code + phone + "@" + sms_gateway
        else:
            raise ValueError(
                f"\n\tcountry code should match the pattern {COUNTRY_CODE.pattern}"
            )
        body = f"\n{message}".encode("ascii", "ignore").decode("ascii")
        subject = subject or f"Message from {self.env.gmail_user}"
        if not self._authenticated:
            status = self.authenticate
            if not status.ok:
                return status
        message = (
            f"From: {self.env.gmail_user}\n"
            + f"To: {to}\n"
            + f"Subject: {subject}\n"
            + body
        )
        if len(message) > 428:
            return Response(
                dictionary={
                    "ok": False,
                    "status": 413,
                    "body": f"Payload length: {len(message):,}, which is more than the optimal size: 428. "
                    f"Message length: {len(body):,}",
                }
            )

        self.server.sendmail(from_addr=self.env.gmail_user, to_addrs=to, msg=message)

        if delete_sent:
            if delete_response := DeleteSent(
                username=self.env.gmail_user,
                password=self.env.gmail_pass,
                subject=subject,
                body=body,
                to=to,
            ).delete_sent():
                return Response(
                    dictionary={
                        "ok": True,
                        "status": 200,
                        "body": f"SMS has been sent to {to}",
                        "extra": delete_response,
                    }
                )
            return Response(
                dictionary={
                    "ok": True,
                    "status": 206,
                    "body": f"SMS has been sent to {to}",
                    "extra": "Failed to locate and delete the SMS from Sent Mail.",
                }
            )
        return Response(
            dictionary={"ok": True, "status": 200, "body": f"SMS has been sent to {to}"}
        )
