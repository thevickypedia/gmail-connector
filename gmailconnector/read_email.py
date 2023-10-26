import base64
import binascii
import email
import imaplib
import socket
import warnings
from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from email.header import decode_header, make_header
from email.message import Message
from typing import Iterable, Union

import pytz
from typing_extensions import Unpack

from .models.config import IngressConfig
from .models.options import Category, Condition
from .models.responder import Email, Response


class ReadEmail:
    """Initiates Emailer object to authenticate and yield the emails according the conditions/filters.

    >>> ReadEmail

    """

    LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo

    def __init__(self, **kwargs: 'Unpack[IngressConfig]'):
        """Initiates necessary args, creates a connection with Gmail host to read emails from the chosen folder.

        Keyword Args:
            gmail_user: Gmail username to authenticate SMTP lib.
            gmail_pass: Gmail password to authenticate SMTP lib.
            timeout: Connection timeout for SMTP lib.
            gmail_host: Hostname for gmail's smtp server.
            folder: Folder where the emails have to be read from.

        References:
            https://imapclient.readthedocs.io/en/2.1.0/_modules/imapclient/imapclient.html#IMAPClient.xlist_folders

        See Also:
            Uses broad ``Exception`` clause to catch login errors, since the same is raised by ``imaplib``
        """
        self.error = None
        self.mail = None
        self._authenticated = False
        self.env = IngressConfig(**kwargs)
        self.create_ssl_connection(gmail_host=self.env.gmail_host, timeout=self.env.timeout)

    def create_ssl_connection(self, gmail_host: str, timeout: Union[int, float]) -> None:
        """Creates an SSL connection to gmail's SSL server."""
        try:
            self.mail = imaplib.IMAP4_SSL(host=gmail_host, port=993, timeout=timeout)
        except socket.error as error:
            self.error = error.__str__()

    @property
    def authenticate(self):
        """Initiates authentication.

        Returns:
            Response:
            A custom response class with properties: ok, status and body to the user.
        """
        if self.mail is None:
            return Response(dictionary={
                'ok': False,
                'status': 408,
                'body': self.error or "failed to create a connection with gmail's SMTP server"
            })
        try:
            self.mail.login(user=self.env.gmail_user, password=self.env.gmail_pass)
            self.mail.list()  # list all the folders within your mailbox (like inbox, sent, drafts, etc)
            self.mail.select(self.env.folder)
            self._authenticated = True
            return Response(dictionary={
                'ok': True,
                'status': 200,
                'body': 'authentication success'
            })
        except Exception as error:
            self.error = error.__str__()
            return Response(dictionary={
                'ok': False,
                'status': 401,
                'body': 'authentication failed'
            })

    def instantiate(self,
                    filters: Union[Iterable[Category.__str__], Iterable[Condition.__str__]] = "UNSEEN") -> Response:
        """Searches the number of emails for the category received and forms.

        Args:
            filters: Category or Condition

        References:
            https://imapclient.readthedocs.io/en/2.1.0/api.html#imapclient.IMAPClient.search

        Returns:
            Response:
            A Response class containing number of email messages, return code and the encoded messages itself.
        """
        if self._authenticated is False:
            status = self.authenticate
            if not status.ok:
                return status
        if type(filters) in (list, tuple):
            filters = ' '.join(filters)
        return_code, messages = self.mail.search(None, filters)
        if return_code != 'OK':
            return Response(dictionary={
                'ok': False,
                'status': 404,
                'body': 'Unable to read emails.'
            })

        num = len(messages[0].split())
        if not num:
            return Response(dictionary={
                'ok': False,
                'status': 204,
                'body': f'No emails found in {self.env.gmail_user} [{self.env.folder}] '
                        f'for the filter(s) {filters.lower()!r}',
                'count': num
            })

        if return_code == 'OK':
            return Response(dictionary={
                'ok': True,
                'status': 200,
                'body': messages,
                'count': num
            })

    def get_info(self, response_part: tuple, dt_flag: bool) -> Email:
        """Extracts sender, subject, body and time received from response part.

        Args:
            response_part: Encoded tuple of the response part in the email.
            dt_flag: Boolean flag whether to convert datetime as human-readable format.

        Returns:
            Email:
            Email object with information.
        """
        original_email = email.message_from_bytes(response_part[1])
        if received := original_email.get('Received'):
            date = received.split(';')[-1].strip()
        else:
            date = original_email.get('Date')
        if '(PDT)' in date:
            datetime_obj = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S -0700 (PDT)")
        elif '(PST)' in date:
            datetime_obj = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S -0800 (PST)")
        else:
            datetime_obj = datetime.now()
        from_ = original_email['From'].split(' <')
        sub = make_header(decode_header(original_email['Subject'])) \
            if original_email['Subject'] else None
        # Converts pacific time to local timezone as the default is pacific
        local_time = datetime_obj.replace(tzinfo=pytz.timezone('US/Pacific')).astimezone(tz=self.LOCAL_TIMEZONE)
        if dt_flag:
            received_date = local_time.strftime("%Y-%m-%d")
            current_date_ = datetime.today().date()
            # Replaces current date with today or yesterday to make it simpler
            if received_date == str(current_date_):
                receive = local_time.strftime("Today, at %I:%M %p")
            elif received_date == str(current_date_ - timedelta(days=1)):
                receive = local_time.strftime("Yesterday, at %I:%M %p")
            else:
                receive = local_time.strftime("on %A, %B %d, at %I:%M %p")
        else:
            receive = local_time
        if original_email.get_content_type() == "text/plain":  # ignore attachments and html
            body = original_email.get_payload(decode=True)
            body = body.decode('utf-8')
        else:
            body = ""
            for payload in original_email.get_payload():
                if isinstance(payload, Message):
                    body += payload.as_string()
                elif isinstance(payload, str):
                    body += payload
                elif isinstance(payload, bytes):
                    try:
                        decoded = base64.b64decode(payload)
                    except binascii.Error:
                        try:
                            decoded = payload.decode()  # encoding is unknown at this point so default to UTF-8
                        except UnicodeDecodeError:
                            warnings.warn(
                                "Unknown encoding type for payload"
                            )
                            continue
                    body += decoded
                else:
                    warnings.warn(
                        f"Unsupported payload type: {type(payload)}"
                    )
        if len(from_) == 1:
            return Email(dictionary=dict(sender=None, sender_email=from_[0].lstrip('<').rstrip('>'),
                                         subject=sub, date_time=receive, body=body))
        return Email(dictionary=dict(sender=from_[0], sender_email=from_[1].rstrip('>'),
                                     subject=sub, date_time=receive, body=body))

    def read_mail(self, messages: list or str, humanize_datetime: bool = False) -> Generator[Email]:
        """Yield emails matching the filters' criteria.

        Args:
            messages: Takes the encoded message list as an argument. This is the body of the ``instantiate`` method.
            humanize_datetime: Converts received time to human-readable format.

        Yields:
            dict:
            A custom response class with properties: ok, status and body to the user.
        """
        for nm in messages[0].split():
            dummy, data = self.mail.fetch(nm, '(RFC822)')
            for each_response in data:
                if isinstance(each_response, tuple):
                    yield self.get_info(response_part=each_response, dt_flag=humanize_datetime)
        else:
            if self.mail:
                self.mail.close()
                self.mail.logout()
