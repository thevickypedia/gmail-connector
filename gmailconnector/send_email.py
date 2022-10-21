import os
from email.mime import multipart, text
from email.mime.application import MIMEApplication
from smtplib import SMTP, SMTPAuthenticationError, SMTPConnectError
from typing import Union

from dotenv import load_dotenv

from .responder import Response

if os.path.isfile('.env'):
    load_dotenv(dotenv_path='.env')


class SendEmail:
    """Initiates Emailer object to email defined recipient from a defined sender with or without attachments.

    >>> SendEmail

    """

    def __init__(self, gmail_user: str = os.environ.get('gmail_user') or os.environ.get('GMAIL_USER'),
                 gmail_pass: str = os.environ.get('gmail_pass') or os.environ.get('GMAIL_PASS')):
        """Initiates necessary args, creates a connection with Gmail's SMTP on port 587.

        Args:
            gmail_user: Login email address.
            gmail_pass: Login password.
        """
        self.server = None
        if not all([gmail_user, gmail_pass]):
            raise ValueError(
                'Cannot proceed without the args: `gmail_user` and `gmail_pass`'
            )
        self.gmail_user = gmail_user
        self.gmail_pass = gmail_pass
        self.server = SMTP(host='smtp.gmail.com', port=587)
        self._authenticated = False

    @property
    def authenticate(self) -> Response:
        """Starts the TLS server and authenticates the user.

        Returns:
            Response:
            A custom response class with properties: ok, status and body to the user.
        """
        self.server.starttls()
        try:
            self.server.login(user=self.gmail_user, password=self.gmail_pass)
            self._authenticated = True
            return Response(dictionary={
                'ok': True,
                'status': 200,
                'body': "Authentication was successful."
            })
        except SMTPAuthenticationError:
            self.server = None
            return Response(dictionary={
                'ok': False,
                'status': 401,
                'body': "GMAIL login failed with SMTPAuthenticationError: Username and Password not accepted.\n"
                        "Ensure the credentials stored in env vars are set correct.\n"
            })
        except SMTPConnectError:
            self.server = None
            return Response(dictionary={
                'ok': False,
                'status': 503,
                'body': "Error during connection establishment with GMAIL server."
            })

    def __del__(self):
        """Destructor has been called to close the TLS connection and logout."""
        if self.server:
            self.server.close()

    def _multipart_message(self, subject: str, recipient: str or list, sender: str, body: str, html_body: str,
                           attachment: str, filename: str, cc: str or list) -> multipart.MIMEMultipart:
        """Creates a multipart message with subject, body, from and to address, and attachment if filename is passed.

        Args:
            recipient: Email address of the recipient to whom the email has to be sent.
            subject: Subject line of the email.
            body: Body of the email. Defaults to ``None``.
            html_body: Body of the email. Defaults to ``None``.
            attachment: Name of the file that has to be attached.
            filename: Custom name of the attachment.
            cc: Email address of the recipient to whom the email has to be CC'd.
            sender: Add sender name to the email.

        Returns a message if a filename is given for attachment but not available at the given path.

        Returns:
            `multipart.MIMEMultipart`:
            MIMEMultipart version of the created message.
        """
        recipient = [recipient] if isinstance(recipient, str) else recipient
        if cc:
            cc = [cc] if isinstance(cc, str) else cc

        msg = multipart.MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"{sender} <{self.gmail_user}>"
        msg['To'] = ','.join(recipient)
        if cc:
            msg['Cc'] = ','.join(cc)

        if body:
            msg.attach(payload=text.MIMEText(body, 'plain'))
        if html_body:
            msg.attach(payload=text.MIMEText(html_body, 'html'))

        if attachment and (os.path.isfile(attachment)):
            file_type = attachment.split('.')[-1]
            if filename and '.' in filename:  # filename is passed with an extn
                pass
            elif filename and '.' in attachment:  # file name's extn is got from attachment name
                filename = f'{filename}.{file_type}'
            elif filename:  # filename is passed without an extn so proceeding with the same
                pass
            else:
                filename = attachment.split(os.path.sep)[-1].strip()  # rips path from attachment as filename
            with open(attachment, 'rb') as attachment:
                attribute = MIMEApplication(attachment.read(), _subtype=file_type)
            attribute.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(payload=attribute)

        return msg

    def send_email(self, subject: str,
                   recipient: Union[str, list] = os.environ.get('recipient') or os.environ.get('RECIPIENT'),
                   sender: str = 'GmailConnector', body: str = None, html_body: str = None, attachment: str = None,
                   filename: str = None, cc: Union[str, list] = None, bcc: Union[str, list] = None) -> Response:
        """Initiates a TLS connection and sends the email.

        Args:
            recipient: Email address of the recipient to whom the email has to be sent.
            subject: Subject line of the email.
            body: Body of the email. Defaults to ``None``.
            html_body: Body of the email. Defaults to ``None``.
            attachment: Name of the file that has to be attached.
            filename: Custom name of the attachment.
            cc: Email address of the recipient to whom the email has to be CC'd.
            bcc: Email address of the recipient to whom the email has to be BCC'd.
            sender: Add sender name to the email.

        Returns:
            Response:
            A custom response class with properties: ok, status and body to the user.
        """
        if not self._authenticated:
            status = self.authenticate
            if not status.ok:
                return status

        msg = self._multipart_message(subject=subject, sender=sender, recipient=recipient, attachment=attachment,
                                      body=body, html_body=html_body, cc=cc, filename=filename)
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
        return_msg = f'Email has been sent to {recipient}'
        if attachment and not os.path.isfile(attachment):
            return Response(dictionary={
                'ok': True,
                'status': 206,
                'body': return_msg + f"\n{attachment} is unavailable at {os.path.realpath(filename='')}.\n"
                                     "Email was sent without an attachment."
            })
        else:
            return Response(dictionary={
                'ok': True,
                'status': 200,
                'body': return_msg
            })
