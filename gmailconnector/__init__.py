"""Place holder for package."""

import os
from typing import Union

import dotenv

from .models.config import Encryption, SMSGateway  # noqa: F401
from .models.options import Category, Condition, Folder  # noqa: F401
from .models.responder import Response  # noqa: F401
from .read_email import ReadEmail  # noqa: F401
from .send_email import SendEmail  # noqa: F401
from .send_sms import SendSMS  # noqa: F401
from .sms_deleter import DeleteSent  # noqa: F401
from .validator.address import EmailAddress  # noqa: F401
from .validator.validate_email import validate_email  # noqa: F401

version = "0.9.1"


def load_env(filename: Union[str, os.PathLike] = ".env", scan: bool = False) -> None:
    """Load .env files."""
    if scan:
        for file in os.listdir():
            if os.path.isfile(file) and file.endswith(".env"):
                dotenv.load_dotenv(dotenv_path=file, verbose=False)
    else:
        if os.path.isfile(filename):
            dotenv.load_dotenv(dotenv_path=filename, verbose=False)


load_env()
