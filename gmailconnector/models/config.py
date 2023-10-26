import os
from enum import Enum
from typing import Union

from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings

from .options import Folder


class Encryption(str, Enum):
    """Enum wrapper for TLS and SSL encryption.

    >>> Encryption

    """

    TLS: str = "TLS"
    SSL: str = "SSL"


class SMSGatewayModel(BaseModel):
    """Wrapper for SMS gateways.

    >>> SMSGatewayModel

    """

    att: str = "mms.att.net"
    tmobile: str = "tmomail.net"
    verizon: str = "vtext.com"
    boost: str = "smsmyboostmobile.com"
    cricket: str = "sms.cricketwireless.net"
    uscellular: str = "email.uscc.net"
    all: tuple = (att, tmobile, verizon, boost, cricket, uscellular)


SMSGateway = SMSGatewayModel()


class EgressConfig(BaseSettings):
    """Configure arguments for ``SendEmail``/``SendSMS`` and validate using ``pydantic`` to share across modules.

    >>> EgressConfig

    """

    gmail_user: EmailStr
    gmail_pass: str
    recipient: Union[EmailStr, None] = None
    phone: Union[str, None] = Field(None, pattern="\\d{10}$")
    gmail_host: str = "smtp.gmail.com"
    encryption: Encryption = Encryption.TLS
    timeout: int = 10

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".env"))
        extra = "allow"


class IngressConfig(BaseSettings):
    """Configure arguments for ``ReadEmail`` and validate using ``pydantic`` to share across modules.

    >>> IngressConfig

    """

    gmail_user: EmailStr
    gmail_pass: str
    folder: Folder = Folder.inbox
    gmail_host: str = "imap.gmail.com"
    timeout: Union[int, float] = 10

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".env"))
        extra = "allow"
