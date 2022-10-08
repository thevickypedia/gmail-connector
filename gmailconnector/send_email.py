import os
from email.mime import multipart, text
from email.mime.application import MIMEApplication
from smtplib import SMTP, SMTPAuthenticationError, SMTPConnectError

from dotenv import load_dotenv

from .responder import Response

if os.path.isfile('.env'):
    load_dotenv(dotenv_path='.env')


class SendEmail:
    """Initiates Emailer object to email defined recipient from a defined sender with or without attachments.

    >>> SendEmail

    """

    def __init__(self, subject: str,
                 gmail_user: str = os.environ.get('gmail_user') or os.environ.get('GMAIL_USER'),
                 gmail_pass: str = os.environ.get('gmail_pass') or os.environ.get('GMAIL_PASS'),
                 recipient: str or list = os.environ.get('recipient') or os.environ.get('RECIPIENT'),
                 sender: str = 'GmailConnector', body: str = None, html_body: str = None,
                 attachment: str = None, filename: str = None,
                 cc: str or list = None, bcc: str or list = None):
        """Initiates all the necessary args.

        Args:
            gmail_user: Login email address.
            gmail_pass: Login password.
            recipient: Email address of the recipient to whom the email has to be sent.
            subject: Subject line of the email.
            body: Body of the email. Defaults to ``None``.
            html_body: Body of the email. Defaults to ``None``.
            attachment: Name of the file that has to be attached.
            filename: Custom name of the attachment.
            cc: Email address of the recipient to whom the email has to be CC'd.
            bcc: Email address of the recipient to whom the email has to be BCC'd.
            sender: Add sender name to the email.
        """
        self.server = None
        if not all([gmail_user, gmail_pass, recipient, subject]):
            raise ValueError(
                'Cannot proceed without the args: `gmail_user`, `gmail_pass`, `recipient` and `subject`'
            )
        self.gmail_user = gmail_user
        self.gmail_pass = gmail_pass
        self.recipient = recipient
        self.subject = subject
        self.cc = cc
        self.bcc = bcc
        self.body = body
        self.html_body = html_body

        self.sender = f"{sender} <{gmail_user}>"
        self.attachment = attachment
        self.filename = filename
        self.server = SMTP(host='smtp.gmail.com', port=587)

    def __del__(self):
        """Destructor has been called to close the TLS connection and logout."""
        if self.server:
            self.server.close()

    def _multipart_message(self) -> multipart.MIMEMultipart:
        """Creates a multipart message with subject, body, from and to address, and attachment if filename is passed.

        Returns a message if a filename is given for attachment but not available at the given path.

        Returns:
            `multipart.MIMEMultipart`:
            MIMEMultipart version of the created message.

        """
        msg = multipart.MIMEMultipart()
        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = ','.join(self.recipient) if isinstance(self.recipient, list) else self.recipient
        if cc := self.cc:
            msg['Cc'] = cc

        if self.body:
            msg.attach(payload=text.MIMEText(self.body, 'plain'))
        if self.html_body:
            msg.attach(payload=text.MIMEText(self.html_body, 'html'))

        if self.attachment and (os.path.isfile(self.attachment)):
            file_type = self.attachment.split('.')[-1]
            if self.filename and '.' in self.filename:  # filename is passed with an extn
                pass
            elif self.filename and '.' in self.attachment:  # file name's extn is got from attachment name
                self.filename = f'{self.filename}.{file_type}'
            elif self.filename:  # filename is passed without an extn so proceeding with the same
                pass
            else:
                self.filename = self.attachment.split(os.path.sep)[-1].strip()  # rips path from attachment as filename
            with open(self.attachment, 'rb') as attachment:
                attribute = MIMEApplication(attachment.read(), _subtype=file_type)
            attribute.add_header('Content-Disposition', 'attachment', filename=self.filename)
            msg.attach(payload=attribute)

        return msg

    def send_email(self) -> Response:
        """Initiates a TLS connection and sends the email.

        Returns:
            Response:
            A custom response class with properties: ok, status and body to the user.
        """
        self.server.starttls()
        try:
            self.server.login(user=self.gmail_user, password=self.gmail_pass)
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

        to = self.recipient
        recipients = [to] if isinstance(to, str) else to

        if cc := self.cc:
            recipients.append(cc) if isinstance(cc, str) else recipients.extend(cc)

        if bcc := self.bcc:
            recipients.append(bcc) if isinstance(bcc, str) else recipients.extend(bcc)

        self.server.sendmail(
            from_addr=self.sender,
            to_addrs=recipients,
            msg=self._multipart_message().as_string()
        )

        return_msg = f'Email has been sent to {self.recipient}'

        if self.attachment and not os.path.isfile(self.attachment):
            return Response(dictionary={
                'ok': True,
                'status': 206,
                'body': return_msg + f"\n{self.attachment} is unavailable at {os.path.realpath(filename='')}.\n"
                                     "Email was sent without an attachment."
            })
        else:
            return Response(dictionary={
                'ok': True,
                'status': 200,
                'body': return_msg
            })


if __name__ == '__main__':
    from datetime import datetime

    response = SendEmail(subject=datetime.now().strftime("%B %d, %Y %I:%M %p")).send_email()

    if response.ok and response.status == 200:
        print('SUCCESS')
    elif response.status == 403:
        print('AUTH ERROR')
    elif response.status == 503:
        print('SERVICE UNAVAILABLE')
    print(response.json())
