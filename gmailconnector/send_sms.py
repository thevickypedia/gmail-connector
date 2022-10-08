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

    def __init__(self, message: str, phone: str = os.environ.get('phone') or os.environ.get('PHONE'),
                 gmail_user: str = os.environ.get('gmail_user') or os.environ.get('GMAIL_USER'),
                 gmail_pass: str = os.environ.get('gmail_pass') or os.environ.get('GMAIL_PASS'),
                 subject: str = None, carrier: str = 't-mobile', sms_gateway: str = None, delete_sent: bool = True):
        """Initiates all the necessary args.

        Args:
            gmail_user: Gmail username to authenticate SMTP lib.
            gmail_pass: Gmail password to authenticate SMTP lib.
            phone: Phone number stored as env var.
            message: Content of the message.
            subject: Subject line for the message. Defaults to "Message from GmailConnector"
            carrier: Takes any of ``at&t``, ``t-mobile``, ``verizon``, ``boost``, ``cricket``, ``us-cellular``
            sms_gateway: Takes the SMS gateway of the carrier as an argument.

        See Also:
            Carrier defaults to ``t-mobile`` which uses ``tmomail.net`` as the SMS gateway.
        """
        self.server, self.mail = None, None
        if not all([gmail_user, gmail_pass, phone, message]):
            raise ValueError(
                'Cannot proceed without the args: `gmail_user`, `gmail_pass`, `phone` and `message`'
            )
        if not gmail_user.endswith('@gmail.com'):
            gmail_user = gmail_user + '@gmail.com'
        self.gmail_user = gmail_user
        self.gmail_pass = gmail_pass
        self.message = message
        self.phone = phone
        self._validate_phone()

        self.body = f'\n\n{message}'.encode('ascii', 'ignore').decode('ascii')
        self.subject = subject or f"Message from {gmail_user.replace('@gmail.com', '')}"
        self.delete_sent = delete_sent

        carrier = carrier.lower()
        if carrier not in list(self.SMS_GATEWAY.keys()):
            carrier = 't-mobile'
        self.gateway = sms_gateway or self.SMS_GATEWAY.get(carrier)

        self.to = self._generate_address()
        self.server = SMTP(host="smtp.gmail.com", port=587)

    def __del__(self):
        """Destructor has been called to close the TLS connection and logout."""
        if self.server:
            self.server.close()

    def _validate_phone(self):
        """Validates all the arguments passed during object initialization.

        Raises:
            ValueError: If any arg is missing or malformed.
        """
        if len(self.phone) != 10 and len(self.phone) != 12:
            raise ValueError('Phone number should either be 10 or 12 digits (if includes country code)')
        if self.phone.startswith('+') and not self.phone.startswith('+1'):
            raise ValueError('Unsupported country code. Module works only for US based contact numbers.')

    def _generate_address(self) -> str:
        """Validates the digits in the phone number and forms the endpoint using the phone number and sms gateway.

        Returns:
            str:
            Returns the formed endpoint. `Example: ``+11234567890@tmomail.net```
        """
        if len(self.phone) == 11 and self.phone.startswith('1'):
            self.phone = f'+{self.phone}'
        if not self.phone.startswith('+'):
            self.phone = f'+1{self.phone}'
        return self.phone + '@' + self.gateway

    def send_sms(self) -> Response:
        """Initiates a TLS connection and sends a text message through SMS gateway of destination number.

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
        message = (f"From: {self.gmail_user}\n" + f"To: {self.to}\n" + f"Subject: {self.subject}\n" + self.body)

        if len(message) > 428:
            return Response(dictionary={
                'ok': False,
                'status': 413,
                'body': f'Payload length: {len(message):,}, which is more than the optimal size: 428. '
                        f'Message length: {len(self.body):,}'
            })

        self.server.starttls()

        try:
            self.server.login(user=self.gmail_user, password=self.gmail_pass)
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

        self.server.sendmail(self.gmail_user, self.to, message)

        if self.delete_sent:
            delete = DeleteSent(username=self.gmail_user, password=self.gmail_pass, subject=self.subject)
            Thread(target=delete.delete_sent, daemon=True).start()

        return Response(dictionary={
            'ok': True,
            'status': 200,
            'body': f'SMS has been sent to {self.to}'
        })


if __name__ == '__main__':
    from datetime import datetime

    response = Messenger(
        message=f'Hello on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}'
    ).send_sms()

    if response.ok and response.status == 200:
        print('SUCCESS')
    else:
        print('FAILED')
    print(response.json())
