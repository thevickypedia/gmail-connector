from smtplib import SMTP, SMTPAuthenticationError, SMTPConnectError


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
        self.message = f'\n\n{message}'
        self.server = SMTP("smtp.gmail.com", 587)

    def __del__(self):
        """Destructor has been called to close the TLS connection and logout."""
        if self.server:
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

        try:
            self.server.login(user=self.username, password=self.password)
        except SMTPAuthenticationError:
            self.server = None
            return_msg = "GMAIL login failed with SMTPAuthenticationError: Username and Password not accepted.\n" \
                         "Ensure the credentials stored in env vars are set correct.\n"
            return {
                'ok': False,
                'status': 401,
                'body': return_msg
            }
        except SMTPConnectError:
            self.server = None
            return_msg = "Error during connection establishment with GMAIL server."
            return {
                'ok': False,
                'status': 503,
                'body': return_msg
            }

        self.server.sendmail(self.username, to, message)

        return_msg = f'SMS has been sent to {to}'
        return {
            'ok': True,
            'status': 200,
            'body': return_msg
        }


if __name__ == '__main__':
    from datetime import datetime
    from os import environ

    response = Messenger(
        gmail_user=environ.get('gmail_user'), gmail_pass=environ.get('gmail_pass'),
        phone_number=environ.get('phone'), message=f'Hello on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}'
    ).send_sms()

    if response.get('ok') and response.get('status') == 200:
        print('SUCCESS')
    else:
        print('FAILED')
