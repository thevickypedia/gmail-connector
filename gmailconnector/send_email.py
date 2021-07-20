from email.mime import multipart, text
from email.mime.application import MIMEApplication
from logging import INFO, basicConfig, getLogger
from pathlib import PurePath
from smtplib import SMTP, SMTPAuthenticationError, SMTPConnectError

basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s', level=INFO)
logger = getLogger(PurePath(__file__).stem)


class SendEmail:
    """Initiates Emailer object to send an email to defined recipient from a defined sender with or without attachments.

    >>> SendEmail

    Args:
        - gmail_user: Username to login to TLS.
        - gmail_pass: Password to authenticate TLS session.
        - recipient: Email address of the recipient to whom the email has to be sent.
        - subject: Subject line of the email.
        - attachment [Optional] : Filename that has to be attached.
        - body [Optional] : Body of the email. Defaults to no body.
        - sender [Optional] : Email address of the sender. Defaults to gmail_user.

    """

    def __init__(self, gmail_user: str, gmail_pass: str, recipient: str, subject: str,
                 attachment: str = None, body: str = None, sender: str = None):
        """Gathers all the necessary parameters to send an email."""
        self.gmail_user = gmail_user
        self.gmail_pass = gmail_pass
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.sender = f"GmailConnector <{sender}>" if sender else f"GmailConnector <{gmail_user}>"
        self.attachment = attachment
        self.server = SMTP('smtp.gmail.com')

    def __del__(self):
        """Destructor has been called to close the TLS connection and logout."""
        if self.server:
            logger.info('Session will be closed and logged out.')
            self.server.quit()

    def multipart_message(self) -> multipart.MIMEMultipart:
        """Creates a multipart message with the subject, body, from and to address, and attachment if passed.

        Returns:
            `multipart.MIMEMultipart`:
            MIMEMultipart version of the created message.

        """
        msg = multipart.MIMEMultipart()
        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = self.recipient

        if body := self.body:
            msg.attach(payload=text.MIMEText(body))

        if filename := self.attachment:
            with open(filename, 'rb') as attachment:
                attribute = MIMEApplication(attachment.read(), _subtype=filename.split('.')[-1])
            attribute.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(payload=attribute)

        return msg

    def send_email(self) -> None:
        """Initiates a TLS connection and sends the email."""
        self.server.starttls()
        try:
            self.server.login(user=self.gmail_user, password=self.gmail_pass)
        except SMTPAuthenticationError:
            self.server = None
            logger.error("GMAIL login failed with SMTPAuthenticationError: Username and Password not accepted.\n"
                         "Ensure the credentials stored in env vars are set correct.\n"
                         "Logon to https://myaccount.google.com/lesssecureapps and turn ON less secure apps.\n"
                         "If 2 factor authentication is enabled, set `gmail_pass` to the generated App Password.\n"
                         "More info: https://support.google.com/mail/?p=BadCredentials")
            return
        except SMTPConnectError:
            self.server = None
            logger.error("Error during connection establishment with GMAIL server.")
            return

        self.server.sendmail(
            from_addr=self.sender,
            to_addrs=[self.recipient],
            msg=self.multipart_message().as_string()
        )

        logger.info(f'Email has been sent to {self.recipient}')


if __name__ == '__main__':
    from datetime import datetime
    from os import environ

    email_obj = SendEmail(
        gmail_user=environ.get('gmail_user'), gmail_pass=environ.get('gmail_pass'), recipient=environ.get('recipient'),
        subject=datetime.now().strftime("%B %d, %Y %I:%M %p"), attachment=None, body=None, sender=None
    )
    print(email_obj.send_email())
