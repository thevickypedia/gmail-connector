"""Place holder for package."""

import os
from typing import NoReturn, Union

import dotenv

from .options import Category, Condition, Folder  # noqa: F401
from .read_email import ReadEmail  # noqa: F401
from .send_email import SendEmail  # noqa: F401
from .send_sms import SendSMS  # noqa: F401

version = "0.7.1"


def load_env(filename: Union[str, os.PathLike] = ".env") -> NoReturn:
    """Load .env files."""
    if os.path.isfile(filename):
        dotenv.load_dotenv(dotenv_path=filename, verbose=False)


load_env()
