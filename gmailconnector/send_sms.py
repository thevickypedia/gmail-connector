from concurrent.futures import ThreadPoolExecutor
from email import message_from_bytes
from email.header import decode_header, make_header
from imaplib import IMAP4_SSL
from smtplib import SMTP, SMTPAuthenticationError, SMTPConnectError
from threading import Thread

from validate_email import validate_email

from gmailconnector.responder import Response


class Messenger:
    """Initiates Messenger object to send an SMS to a phone number using SMS gateway provided by the mobile carrier.

    >>> Messenger

    Args:
        gmail_user: Gmail username to authenticate SMTP lib.
        gmail_pass: Gmail password to authenticate SMTP lib.
        phone_number: Phone number stored as env var.
        message: Content of the message.
        subject [Optional] : Subject line for the message. Defaults to "Message from GmailConnector"
        carrier [Optional]: Takes any of ``at&t``, ``t-mobile``, ``verizon``, ``boost``, ``cricket``, ``us-cellular``
        sms_gateway [Optional]: Takes the SMS gateway of the carrier as an argument.

    See Also:
        Carrier defaults to ``t-mobile`` which uses ``tmomail.net`` as the SMS gateway.
    """

    SMS_GATEWAY = {
        "at&t": "mms.att.net",
        "t-mobile": "tmomail.net",
        "verizon": "vtext.com",
        "boost": "smsmyboostmobile.com",
        "cricket": "sms.cricketwireless.net",
        "us-cellular": "email.uscc.net",
    }

    def __init__(self, gmail_user: str, gmail_pass: str, phone_number: str, message: str,
                 subject: str = None, carrier: str = 't-mobile', sms_gateway: str = None,
                 delete_sent: bool = True):
        if not all([gmail_user, gmail_pass, phone_number, message]):
            raise ValueError(
                'Cannot proceed without the args: `gmail_user`, `gmail_pass`, `phone_number` and `message`'
            )
        self.username = gmail_user
        self.password = gmail_pass
        self.phone = phone_number
        self.delete_sent = delete_sent

        self.subject = subject or "Message from GmailConnector"
        self.body = f'\n\n{message}'.encode('ascii', 'ignore').decode('ascii')
        self.server = SMTP("smtp.gmail.com", 587)

        carrier = carrier.lower()
        if carrier not in list(self.SMS_GATEWAY.keys()):
            carrier = 't-mobile'
        self.gateway = sms_gateway or self.SMS_GATEWAY.get(carrier)

        self.to = self.generate_address()
        self.mail = None

    def __del__(self):
        """Destructor has been called to close the TLS connection and logout."""
        if self.server:
            self.server.close()

    def validator(self) -> bool:
        """Check if the email address generated using the SMS gateway is valid.

        Returns:
            bool:
            Boolean flag.
        """
        return validate_email(
            email_address=self.to,
            check_format=True,
            check_blacklist=True,
            check_dns=True,
            dns_timeout=10,
            check_smtp=True,
            smtp_timeout=10,
            smtp_helo_host=self.gateway,
            smtp_from_address=self.username,
            smtp_skip_tls=False,
            smtp_tls_context=None,
            smtp_debug=False
        )

    def generate_address(self) -> str:
        """Validates the digits in the phone number and forms the endpoint using the phone number and sms gateway.

        Returns:
            str:
            Returns the formed endpoint. `Example: ``+11234567890@tmomail.net```
        """
        if len(self.phone) != 10 or not len(self.phone) != 12:
            raise ValueError('Phone number should either be 10 or 12 digits (if includes country code)')
        if self.phone.startswith('+') and not self.phone.startswith('+1'):
            raise ValueError('Unsupported country code. Module works only for US based contact numbers.')

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
        if not self.validator():
            return Response(dictionary={
                'ok': False,
                'status': 422,
                'body': f'{self.to} was invalid. Please check the sms gateway of your carrier and pass it manually.'
            })

        message = (f"From: {self.username}\n" + f"To: {self.to}\n" + f"Subject: {self.subject}\n" + self.body)
        self.server.starttls()

        try:
            self.server.login(user=self.username, password=self.password)
        except SMTPAuthenticationError:
            self.server = None
            return Response(dictionary={
                'ok': False,
                'status': 401,
                'body': "GMAIL login failed with SMTPAuthenticationError: Username and Password not accepted.\n"
                        "Ensure the credentials stored in env vars are set correct.\n"
            })
        except SMTPConnectError:
            self.server = None
            return Response(dictionary={
                'ok': False,
                'status': 503,
                'body': "Error during connection establishment with GMAIL server."
            })

        self.server.sendmail(self.username, self.to, message)

        if self.delete_sent:
            Thread(target=self._delete_sent, daemon=True).start()

        return Response(dictionary={
            'ok': True,
            'status': 200,
            'body': f'SMS has been sent to {self.to}'
        })

    def _thread_executor(self, item_id):
        """Gets invoked as multi-threading, to check for the message which was just sent and sets the flag as Deleted.

        Args:
            item_id: Takes the ID of the message as an argument.
        """
        dummy, data = self.mail.fetch(item_id, '(RFC822)')
        for response_part in data:
            if not isinstance(response_part, tuple):
                continue
            original_email = message_from_bytes(response_part[1])  # gets the raw content
            sender = str(make_header(decode_header((original_email['From']).split(' <')[0])))
            sub = str(make_header(decode_header(original_email['Subject'])))
            to = str(make_header(decode_header(original_email['To'])))
            if to == self.to and sub == self.subject and sender == self.username:
                self.mail.store(item_id.decode('UTF-8'), '+FLAGS', '\\Deleted')
                self.mail.expunge()
                self.mail.close()
                self.mail.logout()
                break

    def _delete_sent(self):
        """Deletes the email from GMAIL's sent items right after sending the message.

        See Also:
            Invokes ``thread_executor`` with 20 workers to sweep through sent items to delete the email.
        """
        self.mail = IMAP4_SSL('imap.gmail.com')
        self.mail.login(user=self.username, password=self.password)
        self.mail.list()
        self.mail.select('"[Gmail]/Sent Mail"')
        return_code, messages = self.mail.search(None, 'ALL')  # Includes SEEN and UNSEEN, although sent is always SEEN
        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(self._thread_executor, sorted(messages[0].split(), reverse=True))


if __name__ == '__main__':
    from datetime import datetime
    from os import environ

    response = Messenger(
        gmail_user=environ.get('gmail_user'), gmail_pass=environ.get('gmail_pass'),
        phone_number=environ.get('phone'), message=f'Hello on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}'
    ).send_sms()

    if response.ok and response.status == 200:
        print('SUCCESS')
    else:
        print('FAILED')
    print(response.json())
