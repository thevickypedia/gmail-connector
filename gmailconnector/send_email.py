from email.mime import multipart, text
from email.mime.application import MIMEApplication
from logging import INFO, basicConfig, getLogger
from os.path import isfile, realpath
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
        - body [Optional] : Body of the email. Defaults to no body.
        - attachment [Optional] : Filename that has to be attached.
        - cc [Optional]: Email address of the recipient to whom the email has to be CC'd.
        - bcc [Optional]: Email address of the recipient to whom the email has to be BCC'd.

    """

    def __init__(self, gmail_user: str, gmail_pass: str, recipient: str or list,
                 subject: str, body: str = None, attachment: str = None,
                 cc: str or list = None, bcc: str or list = None):
        """Gathers all the necessary parameters to send an email."""
        self.gmail_user = gmail_user
        self.gmail_pass = gmail_pass
        self.recipient = recipient
        self.subject = subject
        self.cc = cc
        self.bcc = bcc
        self.body = body
        self.sender = f"GmailConnector <{gmail_user}>"
        self.attachment = attachment
        self.server = SMTP('smtp.gmail.com')

    def __del__(self):
        """Destructor has been called to close the TLS connection and logout."""
        if self.server:
            logger.info('Session will be closed and logged out.')
            self.server.close()

    def multipart_message(self) -> multipart.MIMEMultipart:
        """Creates a multipart message with subject, body, from and to address, and attachment if filename is passed.

        Logs a message if a filename is given for attachment but not available at the right path.

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

        if body := self.body:
            msg.attach(payload=text.MIMEText(body))

        if (filename := self.attachment) and (isfile(filename)):
            with open(filename, 'rb') as attachment:
                attribute = MIMEApplication(attachment.read(), _subtype=filename.split('.')[-1])
            attribute.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(payload=attribute)
        elif filename:
            logger.warning(f"{filename} is unavailable at {realpath(filename='')}\nProceeding without the attachment.")

        return msg

    def send_email(self) -> dict:
        """Initiates a TLS connection and sends the email.

        Returns:
            dict:
            A dictionary with key-value pairs of ok: bool, status: int and body: str to the user.

        """
        self.server.starttls()
        try:
            self.server.login(user=self.gmail_user, password=self.gmail_pass)
        except SMTPAuthenticationError:
            self.server = None
            return_msg = "GMAIL login failed with SMTPAuthenticationError: Username and Password not accepted.\n" \
                         "Ensure the credentials stored in env vars are set correct.\n" \
                         "Logon to https://myaccount.google.com/lesssecureapps and turn ON less secure apps.\n" \
                         "If 2 factor authentication is enabled, set `gmail_pass` to the generated App Password.\n" \
                         "More info: https://support.google.com/mail/?p=BadCredentials"
            logger.error(return_msg)
            return {
                'ok': False,
                'status': 403,
                'body': return_msg
            }
        except SMTPConnectError:
            self.server = None
            return_msg = "Error during connection establishment with GMAIL server."
            logger.error(return_msg)
            return {
                'ok': False,
                'status': 503,
                'body': return_msg
            }

        to = self.recipient
        recipients = [to] if isinstance(to, str) else to

        if cc := self.cc:
            recipients.append(cc) if isinstance(cc, str) else recipients.extend(cc)

        if bcc := self.bcc:
            recipients.append(bcc) if isinstance(bcc, str) else recipients.extend(bcc)

        self.server.sendmail(
            from_addr=self.sender,
            to_addrs=recipients,
            msg=self.multipart_message().as_string()
        )

        return_msg = f'Email has been sent to {self.recipient}'
        logger.info(return_msg)
        return {
            'ok': True,
            'status': 200,
            'body': return_msg
        }


if __name__ == '__main__':
    from datetime import datetime
    from logging import disable
    from os import environ

    disable()

    response = SendEmail(
        gmail_user=environ.get('gmail_user'), gmail_pass=environ.get('gmail_pass'), recipient=environ.get('recipient'),
        subject=datetime.now().strftime("%B %d, %Y %I:%M %p")
    ).send_email()

    if response.get('ok') and response.get('status') == 200:
        print('SUCCESS')
    elif response.get('status') == 403:
        print('AUTH ERROR')
    elif response.get('status') == 503:
        print('SERVICE UNAVAILABLE')
