"""Options that can be included while reading emails."""

import datetime
from enum import Enum
from typing import Union


class Condition:
    """Wrapper for conditions that can be passed to read email."""

    @staticmethod
    def small(size: int):
        """Condition to retrieve emails smaller than the given size."""
        return 'SMALLER "%d"' % size

    @staticmethod
    def text(text: str):
        """Condition to retrieve emails with the text present."""
        return 'TEXT "%s"' % text

    @staticmethod
    def since(since: Union[str, float, 'datetime.date']):
        """Condition to retrieve emails since a given date."""
        if isinstance(since, datetime.date):
            return 'SINCE "%s"' % since.strftime('%d-%b-%Y')
        return 'SINCE "%s"' % since

    @staticmethod
    def subject(subject: str):
        """Condition to retrieve emails with a particular subject."""
        return 'SUBJECT "%s"' % subject


class Folder(str, Enum):
    """Wrapper for folders to choose emails from."""

    inbox: str = "inbox"
    important: str = '"[Gmail]/Important"'
    starred: str = '"[Gmail]/Starred"'
    all: str = '"[Gmail]/All Mail"'
    sent: str = '"[Gmail]/Sent Mail"'
    drafts: str = '"[Gmail]/Drafts"'
    spam: str = '"[Gmail]/Spam"'
    trash: str = '"[Gmail]/Trash"'


class Category:
    """Wrapper for email category."""

    all: str = "ALL"
    seen: str = "SEEN"
    unseen: str = "UNSEEN"
    flagged: str = "FLAGGED"
    not_deleted: str = "NOT DELETED"
