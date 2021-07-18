from smtplib import SMTP


class Messenger:
    """Initiates Messenger object to send an SMS to a phone number using SMS gateway of destination number.

    >>> Messenger

        Args:
            - gmail_user: Gmail username to authenticate SMTP lib.
            - gmail_pass: Gmail password to authenticate SMTP lib.
            - phone_number: Phone number stored as env var.
            - subject `[Optional]` : Subject line for the message. Defaults to "Message from GmailConnector"
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
        print('Session will be closed and logged out.')
        self.server.close()

    def send_sms(self) -> str:
        """Initiates a TLS connection and sends a text message through SMS gateway of destination number.

        Raises:
            UnicodeEncodeError

        See Also:
            - Encodes body of the message to `ascii` with `ignore` flag and then decodes it.
            - This is done to ignore special characters (like °) without raising `UnicodeEncodeError`

        Notes:
            Other flags that can be set includes `replace` and `xmlcharrefreplace`

        Returns:
            `str`:
            Status of the SMS.

        """
        subject = "Message from GmailConnector" if not self.subject else self.subject
        body = self.message.encode('ascii', 'ignore').decode('ascii')
        to = f"{self.phone_number}@tmomail.net"
        message = (f"From: {self.username}\n" + f"To: {to}\n" + f"Subject: {subject}\n" + body)

        self.server.starttls()
        self.server.login(user=self.username, password=self.password)
        self.server.sendmail(self.username, to, message)

        return f'SMS has been sent to {to}'


if __name__ == '__main__':
    from os import environ
    from datetime import datetime

    messenger = Messenger(
        gmail_user=environ.get('gmail_user'), gmail_pass=environ.get('gmail_pass'),
        phone_number=environ.get('phone'), message=f'Hello on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}'
    )
    print(messenger.send_sms())
