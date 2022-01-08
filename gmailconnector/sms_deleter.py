from concurrent.futures import ThreadPoolExecutor
from email import message_from_bytes
from email.header import decode_header, make_header
from imaplib import IMAP4_SSL


class DeleteSent:
    """Initiates DeleteSent object to delete a particular email from SentItems.

    >>> DeleteSent

    """

    def __init__(self, username: str, password: str, subject: str):
        self.mail = IMAP4_SSL('imap.gmail.com')
        self.username = username
        self.subject = subject
        self.mail.login(user=username, password=password)

    def _thread_executor(self, item_id: bytes or str) -> None:
        """Gets invoked in multiple threads, to set the flag as ``Deleted`` for the message which was just sent.

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
            if to == to and sub == self.subject and sender == self.username:
                self.mail.store(item_id.decode('UTF-8'), '+FLAGS', '\\Deleted')
                self.mail.expunge()
                self.mail.close()
                self.mail.logout()
                break

    def delete_sent(self):
        """Deletes the email from GMAIL's sent items right after sending the message.

        See Also:
            Invokes ``thread_executor`` with 20 workers to sweep through sent items to delete the email.
        """
        self.mail.list()
        self.mail.select('"[Gmail]/Sent Mail"')
        return_code, messages = self.mail.search(None, 'ALL')  # Includes SEEN and UNSEEN, although sent is always SEEN
        if return_code != 'OK':
            return
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.map(self._thread_executor, sorted(messages[0].split(), reverse=True))
