import os
import smtplib
import socket
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Union

from typing_extensions import Unpack

from .models.config import EgressConfig, Encryption
from .models.responder import Response
from .validator.address import EmailAddress


def validate_email(address: Union[str, list]) -> Union[str, list]:
    """Validates email addresses and returns them as is."""
    if isinstance(address, str):
        return EmailAddress(address).email
    else:
        return [EmailAddress(addr).email for addr in address]


class SendEmail:
    """Initiates Emailer object to email defined recipient from a defined sender with or without attachments.

    >>> SendEmail

    """

    def __init__(self, **kwargs: 'Unpack[EgressConfig]'):
        """Initiates necessary args, creates a connection with Gmail host based on chosen encryption type.

        Keyword Args:
            gmail_user: Gmail username to authenticate SMTP lib.
            gmail_pass: Gmail password to authenticate SMTP lib.
            timeout: Connection timeout for SMTP lib.
            encryption: Type of encryption to be used.
            gmail_host: Hostname for gmail's smtp server.
        """
        self.server, self.error = None, None
        self.env = EgressConfig(**kwargs)
        self._failed_attachments = {"FILE NOT FOUND": [], "FILE SIZE OVER 25 MB": []}
        self._authenticated = False
        if self.env.encryption == Encryption.TLS:
            self.create_tls_connection(host=self.env.gmail_host, timeout=self.env.timeout)
        else:
            self.create_ssl_connection(host=self.env.gmail_host, timeout=self.env.timeout)

    def create_ssl_connection(self, host: str, timeout: Union[int, float]) -> None:
        """Create a connection using SSL encryption."""
        try:
            self.server = smtplib.SMTP_SSL(host=host, port=465, timeout=timeout)
        except (smtplib.SMTPException, socket.error) as error:
            self.error = error.__str__()

    def create_tls_connection(self, host: str, timeout: Union[int, float]) -> None:
        """Create a connection using TLS encryption."""
        try:
            self.server = smtplib.SMTP(host=host, port=587, timeout=timeout)
            self.server.starttls()
        except (smtplib.SMTPException, socket.error) as error:
            self.error = error.__str__()

    @property
    def authenticate(self) -> Response:
        """Initiates authentication.

        Returns:
            Response:
            A custom response class with properties: ok, status and body to the user.
        """
        if self.server is None:
            return Response(dictionary={
                'ok': False,
                'status': 408,
                'body': self.error or "failed to create a connection with gmail's SMTP server"
            })
        try:
            self.server.login(user=self.env.gmail_user, password=self.env.gmail_pass)
            self._authenticated = True
            return Response(dictionary={
                'ok': True,
                'status': 200,
                'body': 'authentication success'
            })
        except smtplib.SMTPAuthenticationError:
            return Response(dictionary={
                'ok': False,
                'status': 401,
                'body': 'authentication failed'
            })
        except smtplib.SMTPException as error:
            return Response(dictionary={
                'ok': False,
                'status': 503,
                'body': error.__str__()
            })

    def __del__(self):
        """Destructor has been called to close the connection and logout."""
        if self.server:
            self.server.close()

    def multipart_message(self, subject: str, recipient: str or list, sender: str, body: str, html_body: str,
                          attachments: list, filenames: list, cc: str or list) -> MIMEMultipart:
        """Creates a multipart message with subject, body, from and to address, and attachment if filename is passed.

        Args:
            recipient: Email address of the recipient to whom the email has to be sent.
            subject: Subject line of the email.
            body: Body of the email. Defaults to ``None``.
            html_body: Body of the email. Defaults to ``None``.
            attachments: Names of the files that has to be attached.
            filenames: Custom names of the attachments.
            cc: Email address of the recipient to whom the email has to be CC'd.
            sender: Add sender name to the email.

        Returns a message if a filename is given for attachment but not available at the given path.

        Returns:
            `multipart.MIMEMultipart`:
            MIMEMultipart version of the created message.
        """
        recipient = [recipient] if isinstance(recipient, str) else recipient
        cc = [cc] if cc and isinstance(cc, str) else cc

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"{sender} <{self.env.gmail_user}>"
        msg['To'] = ','.join(recipient)
        if cc:
            msg['Cc'] = ','.join(cc)

        if body:
            msg.attach(payload=MIMEText(body, 'plain'))
        if html_body:
            msg.attach(payload=MIMEText(html_body, 'html'))

        for index, attachment_ in enumerate(attachments):
            file_type = attachment_.split('.')[-1]
            try:
                filename = filenames[index]
            except IndexError:
                filename = None
            if filename and '.' in filename:  # filename is passed with an extn
                pass
            elif filename and '.' in attachment_:  # file name's extn is got from attachment name
                filename = f'{filename}.{file_type}'
            elif filename:  # filename is passed without an extn so proceeding with the same
                pass
            else:
                filename = attachment_.split(os.path.sep)[-1].strip()  # rips path from attachment as filename

            if not os.path.isfile(attachment_):
                self._failed_attachments["FILE NOT FOUND"].append(filename)
                continue
            if os.path.getsize(attachment_) / 1e+6 > 25:
                self._failed_attachments["FILE SIZE OVER 25 MB"].append(filename)
                continue

            with open(attachment_, 'rb') as file:
                attribute = MIMEApplication(file.read(), _subtype=file_type)
            attribute.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(payload=attribute)

        return msg

    def send_email(self, subject: str, recipient: Union[str, list],
                   sender: str = 'GmailConnector', body: str = None, html_body: str = None,
                   attachment: Union[str, list] = None, filename: Union[str, list] = None,
                   custom_attachment: Dict[Union[str, os.PathLike], str] = None,
                   cc: Union[str, list] = None, bcc: Union[str, list] = None,
                   fail_if_attach_fails: bool = True) -> Response:
        """Initiates a TLS connection and sends the email.

        Args:
            recipient: Email address of the recipient to whom the email has to be sent.
            subject: Subject line of the email.
            body: Body of the email. Defaults to ``None``.
            html_body: Body of the email. Defaults to ``None``.
            attachment: Name of the file that has to be attached.
            filename: Custom name of the attachment.
            custom_attachment: Dictionary of the filepath as key and the custom name for the attachment as value.
            cc: Email address of the recipient to whom the email has to be CC'd.
            bcc: Email address of the recipient to whom the email has to be BCC'd.
            sender: Add sender name to the email.
            fail_if_attach_fails: Boolean flag to restrict sending the email if attachment is included but fails.

        Returns:
            Response:
            A custom response class with properties: ok, status and body to the user.
        """
        recipient = validate_email(address=recipient)
        cc = validate_email(address=cc) if cc else None
        bcc = validate_email(address=bcc) if bcc else None
        if not self._authenticated:
            status = self.authenticate
            if not status.ok:
                return status
        if custom_attachment:
            attachments = list(custom_attachment.keys())
            filenames = list(custom_attachment.values())
        else:
            attachments = [attachment] if isinstance(attachment, str) else attachment if attachment else []
            filenames = [filename] if isinstance(filename, str) else filename if filename else []

        msg = self.multipart_message(subject=subject, sender=sender, recipient=recipient, attachments=attachments,
                                     body=body, html_body=html_body, cc=cc, filenames=filenames)

        unattached = {k: ', '.join(v) for k, v in self._failed_attachments.items() if v}
        if fail_if_attach_fails and unattached:
            return Response(dictionary={
                'ok': False,
                'status': 422,
                'body': f"Email was not sent. Unattached: {unattached!r}"
            })

        recipients = [recipient] if isinstance(recipient, str) else recipient
        if cc:
            recipients.append(cc) if isinstance(cc, str) else recipients.extend(cc)
        if bcc:
            recipients.append(bcc) if isinstance(bcc, str) else recipients.extend(bcc)
        self.server.sendmail(
            from_addr=sender,
            to_addrs=recipients,
            msg=msg.as_string()
        )
        if unattached:
            return Response(dictionary={
                'ok': True,
                'status': 206,
                'body': f"Email has been sent to {recipient!r}. Unattached: {unattached!r}."
            })
        else:
            return Response(dictionary={
                'ok': True,
                'status': 200,
                'body': f"Email has been sent to {recipient!r}"
            })
