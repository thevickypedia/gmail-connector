import os
from smtplib import SMTP, SMTPAuthenticationError, SMTPConnectError
from threading import Thread

from dotenv import load_dotenv

from .responder import Response
from .sms_deleter import DeleteSent

if os.path.isfile('.env'):
    load_dotenv(dotenv_path='.env')


class Messenger:
    """Initiates Messenger object to send an SMS to a phone number using SMS gateway provided by the mobile carrier.

    >>> Messenger

    """

    SMS_GATEWAY = {
        "at&t": "mms.att.net",
        "t-mobile": "tmomail.net",
        "verizon": "vtext.com",
        "boost": "smsmyboostmobile.com",
        "cricket": "sms.cricketwireless.net",
        "us-cellular": "email.uscc.net",
    }

    def __init__(self, gmail_user: str = os.environ.get('gmail_user') or os.environ.get('GMAIL_USER'),
                 gmail_pass: str = os.environ.get('gmail_pass') or os.environ.get('GMAIL_PASS')):
        """Initiates all the necessary args.

        Args:
            gmail_user: Gmail username to authenticate SMTP lib.
            gmail_pass: Gmail password to authenticate SMTP lib.

        See Also:
            Carrier defaults to ``t-mobile`` which uses ``tmomail.net`` as the SMS gateway.
        """
        self.server, self.mail = None, None
        if not all([gmail_user, gmail_pass]):
            raise ValueError(
                'Cannot proceed without the args: `gmail_user` and `gmail_pass`'
            )
        if not gmail_user.endswith('@gmail.com'):
            gmail_user = gmail_user + '@gmail.com'
        self.gmail_user = gmail_user
        self.gmail_pass = gmail_pass
        self.server = SMTP(host="smtp.gmail.com", port=587)
        self._authenticated = False

    @property
    def authenticate(self) -> Response:
        """Starts the TLS server and authenticates the user.

        Returns:
            Response:
            A custom response class with properties: ok, status and body to the user.
        """
        self.server.starttls()
        try:
            self.server.login(user=self.gmail_user, password=self.gmail_pass)
            self._authenticated = True
            return Response(dictionary={
                'ok': True,
                'status': 200,
                'body': "Authentication was successful."
            })
        except SMTPAuthenticationError:
            return Response(dictionary={
                'ok': False,
                'status': 401,
                'body': "GMAIL login failed with SMTPAuthenticationError: Username and Password not accepted.\n"
                        "Ensure the credentials stored in env vars are set correct.\n"
            })
        except SMTPConnectError:
            return Response(dictionary={
                'ok': False,
                'status': 503,
                'body': "Error during connection establishment with GMAIL server."
            })

    def __del__(self):
        """Destructor has been called to close the TLS connection and logout."""
        if self.server:
            self.server.close()

    @staticmethod
    def _validate_phone(phone):
        """Validates all the arguments passed during object initialization.

        Raises:
            ValueError: If any arg is missing or malformed.
        """
        if len(phone) != 10 and len(phone) != 12:
            raise ValueError('Phone number should either be 10 or 12 digits (if includes country code)')
        if phone.startswith('+') and not phone.startswith('+1'):
            raise ValueError('Unsupported country code. Module works only for US based contact numbers.')

    @staticmethod
    def _generate_address(phone, gateway) -> str:
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

    def send_sms(self, message: str, phone: str = os.environ.get('phone') or os.environ.get('PHONE'),
                 subject: str = None, carrier: str = 't-mobile', sms_gateway: str = None,
                 delete_sent: bool = True) -> Response:
        """Initiates a TLS connection and sends a text message through SMS gateway of destination number.

        Args:
            phone: Phone number stored as env var.
            message: Content of the message.
            subject: Subject line for the message. Defaults to "Message from GmailConnector"
            carrier: Takes any of ``at&t``, ``t-mobile``, ``verizon``, ``boost``, ``cricket``, ``us-cellular``
            sms_gateway: Takes the SMS gateway of the carrier as an argument.
            delete_sent: Boolean flag to delete the message from GMAIL's sent items. Defaults to ``True``.

        Raises:
            UnicodeEncodeError

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
        carrier = carrier.lower()
        if carrier not in list(self.SMS_GATEWAY.keys()):
            carrier = 't-mobile'
        gateway = sms_gateway or self.SMS_GATEWAY.get(carrier)

        self._validate_phone(phone=phone)
        body = f'\n\n{message}'.encode('ascii', 'ignore').decode('ascii')
        subject = subject or f"Message from {self.gmail_user.replace('@gmail.com', '')}"
        to = self._generate_address(phone=phone, gateway=gateway)
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

        self.server.sendmail(self.gmail_user, to, message)

        if delete_sent:
            delete = DeleteSent(username=self.gmail_user, password=self.gmail_pass, subject=subject)
            Thread(target=delete.delete_sent, daemon=True).start()

        return Response(dictionary={
            'ok': True,
            'status': 200,
            'body': f'SMS has been sent to {to}'
        })
