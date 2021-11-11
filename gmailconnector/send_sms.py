from concurrent.futures import ThreadPoolExecutor
from email import message_from_bytes
from email.header import decode_header, make_header
from imaplib import IMAP4_SSL
from smtplib import SMTP, SMTPAuthenticationError, SMTPConnectError
from threading import Thread

from gmailconnector.responder import Response


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
        self.mail = None
        self.subject = "Message from GmailConnector" if not subject else subject
        self.body = f'\n\n{message}'.encode('ascii', 'ignore').decode('ascii')
        self.to = f"{phone_number}@tmomail.net"
        self.server = SMTP("smtp.gmail.com", 587)

    def __del__(self):
        """Destructor has been called to close the TLS connection and logout."""
        if self.server:
            self.server.close()

    def send_sms(self) -> Response:
        """Initiates a TLS connection and sends a text message through SMS gateway of destination number.

        Raises:
            UnicodeEncodeError

        See Also:
            - Encodes body of the message to `ascii` with `ignore` flag and then decodes it.
            - This is done to ignore special characters (like °) without raising `UnicodeEncodeError`

        Notes:
            Other flags that can be set includes `replace` and `xmlcharrefreplace`

        Returns:
            Response:
            A custom response class with properties: ok, status and body to the user.
        """
        message = (f"From: {self.username}\n" + f"To: {self.to}\n" + f"Subject: {self.subject}\n" + self.body)
        self.server.starttls()

        try:
            self.server.login(user=self.username, password=self.password)
        except SMTPAuthenticationError:
            self.server = None
            return_msg = "GMAIL login failed with SMTPAuthenticationError: Username and Password not accepted.\n" \
                         "Ensure the credentials stored in env vars are set correct.\n"
            return Response(dictionary={
                'ok': False,
                'status': 401,
                'body': return_msg
            })
        except SMTPConnectError:
            self.server = None
            return_msg = "Error during connection establishment with GMAIL server."
            return Response(dictionary={
                'ok': False,
                'status': 503,
                'body': return_msg
            })

        self.server.sendmail(self.username, self.to, message)

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
            original_email = message_from_bytes(response_part[1])  # gets the rawest content
            sender = str(make_header(decode_header((original_email['From']).split(' <')[0])))
            sub = str(make_header(decode_header(original_email['Subject'])))
            to = str(make_header(decode_header(original_email['To'])))
            if to == self.to and sub == self.subject and sender == self.username:
                self.mail.store(item_id.decode('UTF-8'), '+FLAGS', '\\Deleted')
                self.mail.expunge()
                self.mail.close()
                self.mail.logout()

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
