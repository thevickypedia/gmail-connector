from enum import Enum


class Encryption(str, Enum):
    """Enum wrapper for TLS and SSL encryption."""

    TLS: str = "TLS"
    SSL: str = "SSL"


class SMSGateway:
    """Enum wrapper for different SMS gateways."""

    att: str = "mms.att.net"
    tmobile: str = "tmomail.net"
    verizon: str = "vtext.com"
    boost: str = "smsmyboostmobile.com"
    cricket: str = "sms.cricketwireless.net"
    uscellular: str = "email.uscc.net"
    all: tuple = (att, tmobile, verizon, boost, cricket, uscellular)
