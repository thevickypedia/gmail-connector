import email.header
import os
from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from imaplib import IMAP4_SSL
from typing import Iterable, Union

import pytz
from dotenv import load_dotenv

from .options import Category, Condition, Folder
from .responder import Email, Response

if os.path.isfile('.env'):
    load_dotenv(dotenv_path='.env')


class ReadEmail:
    """Initiates Emailer object to authenticate and yield the unread emails.

    >>> ReadEmail

    """

    LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo

    def __init__(self, gmail_user: str = os.environ.get('gmail_user') or os.environ.get('GMAIL_USER'),
                 gmail_pass: str = os.environ.get('gmail_pass') or os.environ.get('GMAIL_PASS'),
                 folder: Folder.__str__ = 'inbox'):
        """Initiates all the necessary args.

        Args:
            gmail_user: Login email address.
            gmail_pass: Login password.
            folder: Folder where the unread emails have to be read from.

        References:
            https://imapclient.readthedocs.io/en/2.1.0/_modules/imapclient/imapclient.html#IMAPClient.xlist_folders

        See Also:
            Uses broad ``Exception`` clause to catch login errors, since the same is raised by ``imaplib``
        """
        self.folder = folder
        self.mail = None
        if not all([gmail_user, gmail_pass]):
            raise ValueError(
                'Cannot proceed without the args or env vars: `gmail_user` and `gmail_pass`'
            )
        self.mail = IMAP4_SSL('imap.gmail.com')  # connects to gmail using imaplib
        # noinspection PyBroadException
        try:
            self.mail.login(user=gmail_user, password=gmail_pass)  # login to your gmail account using the env variables
            self.mail.list()  # list all the folders within your mailbox (like inbox, sent, drafts, etc)
            self.mail.select(folder)
        except Exception:
            self.mail = None
        self.gmail_user = gmail_user

    def instantiate(self, filters: Iterable[Union[Category.__str__, Condition.__str__]] = 'UNSEEN') -> Response:
        """Searches the number of emails for the category received and forms.

        Args:
            filters: Category or search criteria.

        References:
            - Categories, ``SMALLER``, ``TEXT``, and ``SINCE`` take additional values.

        Examples:
            ``'SMALLER 500'``
            ``'TEXT "foo-bar"'``
            ``'SINCE 17-Feb-2022'`` [OR] ``'SINCE 1645300995.231752'``

        References:
            https://imapclient.readthedocs.io/en/2.1.0/api.html#imapclient.IMAPClient.search

        Returns:
            Response:
            A Response class containing number of email messages, return code and the encoded messages itself.
        """
        if not self.mail:
            return Response(dictionary={
                'ok': False,
                'status': 401,
                'body': 'BUMMER! Unable to read your emails.\n\nTroubleshooting Steps:\n'
                        '\t1. Make sure your username and password are correct.\n'
                        '\t2. Enable 2 factor authentication and use thee App Specific Password generated.'
            })

        if isinstance(filters, list) or isinstance(filters, tuple):
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
                'body': f'No {filters.lower()!r} emails found for {self.gmail_user} in {self.folder}',
                'count': num
            })

        if return_code == 'OK':
            return Response(dictionary={
                'ok': True,
                'status': 200,
                'body': messages,
                'count': num
            })

    def _get_info(self, response_part: tuple, dt_flag: bool) -> Email:
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
        sub = email.header.make_header(email.header.decode_header(original_email['Subject'])) \
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
        body = None
        if original_email.get_content_type() == "text/plain":  # ignore attachments and html
            body = original_email.get_payload(decode=True)
            body = body.decode('utf-8')
        return Email(dictionary=dict(sender=from_[0], sender_email=from_[1].rstrip('>'), subject=sub,
                                     date_time=receive, body=body))

    def read_mail(self, messages: list or str, humanize_datetime: bool = False) -> Generator[Email]:
        """Prints unread emails one by one after getting user confirmation.

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
                    yield self._get_info(response_part=each_response, dt_flag=humanize_datetime)
        else:  # Executes when there is no break statement in the loop above
            if self.mail:
                self.mail.close()
                self.mail.logout()
