from logging import INFO, basicConfig, getLogger
from pathlib import PurePath
from smtplib import SMTP

basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s', level=INFO)
logger = getLogger(PurePath(__file__).stem)


class Messenger:
    """Initiates Messenger object to send an SMS to a phone number using SMS gateway of destination number.

    >>> Messenger

    Args:
        - gmail_user: Gmail username to authenticate SMTP lib.
        - gmail_pass: Gmail password to authenticate SMTP lib.
        - phone_number: Phone number stored as env var.
        - subject [Optional] : Subject line for the message. Defaults to "Message from GmailConnector"
        - message: Content of the message.
    """

    def __init__(self, gmail_user: str, gmail_pass: str, phone_number: str, message: str,
                 subject: str = None):
        self.username = gmail_user
        self.password = gmail_pass
        self.phone_number = phone_number
        self.subject = subject
        self.message = message
        self.server = SMTP("smtp.gmail.com", 587)

    def __del__(self):
        """Destructor has been called to close the TLS connection and logout."""
        logger.info('Session will be closed and logged out.')
        self.server.close()

    def send_sms(self) -> dict:
        """Initiates a TLS connection and sends a text message through SMS gateway of destination number.

        Raises:
            UnicodeEncodeError

        See Also:
            - Encodes body of the message to `ascii` with `ignore` flag and then decodes it.
            - This is done to ignore special characters (like °) without raising `UnicodeEncodeError`

        Notes:
            Other flags that can be set includes `replace` and `xmlcharrefreplace`

        Returns:
            dict:
            A dictionary with key-value pairs of ok: bool, status: int and body: str to the user.

        """
        subject = "Message from GmailConnector" if not self.subject else self.subject
        body = self.message.encode('ascii', 'ignore').decode('ascii')
        to = f"{self.phone_number}@tmomail.net"
        message = (f"From: {self.username}\n" + f"To: {to}\n" + f"Subject: {subject}\n" + body)

        self.server.starttls()
        self.server.login(user=self.username, password=self.password)
        self.server.sendmail(self.username, to, message)

        return_msg = f'SMS has been sent to {to}'
        logger.info(return_msg)
        return {
            'ok': True,
            'status': 200,
            'body': return_msg
        }


if __name__ == '__main__':
    from datetime import datetime
    from logging import disable
    from os import environ

    disable()

    response = Messenger(
        gmail_user=environ.get('gmail_user'), gmail_pass=environ.get('gmail_pass'),
        phone_number=environ.get('phone'), message=f'Hello on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}'
    ).send_sms()

    if response.get('ok') and response.get('status') == 200:
        print('SUCCESS')
    else:
        print('FAILED')
