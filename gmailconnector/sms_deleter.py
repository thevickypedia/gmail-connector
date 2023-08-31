import email
import imaplib
from concurrent.futures import ThreadPoolExecutor
from email.header import decode_header, make_header
from typing import Dict, Union


class DeleteSent:
    """Initiates DeleteSent object to delete the sent SMS email from SentItems.

    >>> DeleteSent

    """

    def __init__(self, **kwargs):
        """Instantiate the members from kwargs."""
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.subject = kwargs.get('subject')
        self.body = kwargs.get('body')
        self.to = kwargs.get('to')
        self.mail = None
        self.error = None
        self.create_ssl_connection()

    def create_ssl_connection(self) -> None:
        """Create a connection using SSL encryption."""
        try:
            self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
            self.mail.login(user=self.username, password=self.password)
            self.mail.list()
            self.mail.select('"[Gmail]/Sent Mail"')
        except Exception as error:
            self.error = error.__str__()

    def thread_executor(self, item_id: bytes or str) -> Dict[str, str]:
        """Gets invoked in multiple threads, to set the flag as ``Deleted`` for the message which was just sent.

        Args:
            item_id: Takes the ID of the message as an argument.
        """
        dummy, data = self.mail.fetch(item_id, '(RFC822)')
        for response_part in data:
            if not isinstance(response_part, tuple):
                continue
            original_email = email.message_from_bytes(response_part[1])  # gets the raw content
            sender = str(make_header(decode_header((original_email['From']).split(' <')[0])))
            sub = str(make_header(decode_header(original_email['Subject'])))
            to = str(make_header(decode_header(original_email['To'])))
            if to == self.to and sub == self.subject and sender == self.username and \
                    original_email.__dict__.get('_payload', '').strip() == self.body.strip():
                self.mail.store(item_id.decode('UTF-8'), '+FLAGS', '\\Deleted')
                self.mail.expunge()
                return dict(msg_id=original_email['Message-ID'],
                            msg_context=" ".join(original_email['Received'].split()))

    def delete_sent(self) -> Union[Dict[str, str], None]:
        """Deletes the email from GMAIL's sent items right after sending the message.

        See Also:
            Invokes ``thread_executor`` to sweep through sent items to delete the email.

        Warnings:
            Deletion time depends on the number of existing emails in the ``Sent`` folder.
        """
        if self.mail is None:
            return
        return_code, messages = self.mail.search(None, 'ALL')  # Includes SEEN and UNSEEN, although sent is always SEEN
        if return_code != 'OK':
            return
        with ThreadPoolExecutor(max_workers=1) as executor:
            for deleted in executor.map(self.thread_executor, sorted(messages[0].split(), reverse=True)):
                if deleted:  # Indicates the message sent has been deleted, so no need to loop through entire sent items
                    executor.shutdown(cancel_futures=True)
                    self.mail.close()
                    self.mail.logout()
                    return deleted
