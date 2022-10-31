import subprocess
from typing import List

from .exceptions import InvalidDomain, NotMailServer
from .support import hostname_to_ip, matrix_to_flat_list, remove_duplicates


def get_mx_records(domain: str) -> List:
    """Get MX (Mail Exchange server) records for the given domain.

    Args:
        domain: FQDN (Fully Qualified Domain Name) extracted from the email address.

    Returns:
        list:
        List of IP addresses of all the mail exchange servers from authoritative/non-authoritative answer section.
    """
    try:
        output = subprocess.check_output(f'nslookup -q=mx {domain}', shell=True)
        result = [hostname_to_ip(hostname=line.split()[-1]) for line in output.decode().splitlines()
                  if line.startswith(domain)]
        cleaned = remove_duplicates(input_=matrix_to_flat_list(input_=result))
        if not cleaned:
            raise NotMailServer(f"Domain {domain!r} is not a mail server.")
        return cleaned
    except subprocess.CalledProcessError:
        raise InvalidDomain(f"Domain {domain!r} is invalid.")
