import smtplib
import socket


def is_port_allowed(host: str = 'gmail.com', port: int = smtplib.SMTP_PORT, timeout: int = 3):
    """Replicates ``telnet`` command by trying to create a socket connection on a particular host and port.

    Args:
        host: Host that has to be tried. Defaults to 'gmail.com'
        port: Port number that has to be checked. Defaults to SMTP port 25.
        timeout: Timeout for socket connection.

    Returns:
        bool:
        Boolean flag to indicate whether the port is allowed.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    if sock.connect_ex((host, port)) == 0:
        sock.close()
        return True
    sock.close()
