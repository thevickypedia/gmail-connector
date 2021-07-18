from email.mime import multipart, text
from email.mime.application import MIMEApplication
from smtplib import SMTP, SMTPAuthenticationError, SMTPConnectError


class Emailer:
    """Initiates Emailer object to send an email to defined recipient from a defined sender with or without attachments.

    >>> Emailer

        Args:
            - gmail_user: Username to login to TLS.
            - gmail_pass: Password to authenticate TLS session.
            - recipient: Email address of the recipient to whom the email has to be sent.
            - subject: Subject line of the email.
            - attachment: Filename that has to be attached.
            - body: Body of the email.
            - sender: Email address of the sender. Defaults to gmail_user.

    """

    def __init__(self, gmail_user: str, gmail_pass: str, recipient: str, subject: str, attachment: str, body: str,
                 sender: str = None):
        """Gathers all the necessary parameters to send an email."""
        self.gmail_user = gmail_user
        self.gmail_pass = gmail_pass
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.sender = f"PersonalCloud <{sender}>" if sender else f"PersonalCloud <{gmail_user}>"
        self.attachment = attachment

    def multipart_message(self) -> multipart.MIMEMultipart:
        """Creates a multipart message with the subject, body, from and to address, and attachment if passed.

        Returns:
            multipart.MIMEMultipart:
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

    def send_email(self) -> str:
        """Initiates a TLS connection and sends the email.

        Returns:
            str:
            Status of the email message.

        """
        server = SMTP('smtp.gmail.com')
        server.starttls()
        try:
            server.login(user=self.gmail_user, password=self.gmail_pass)
        except SMTPAuthenticationError:
            return "GMAIL login failed with SMTPAuthenticationError: Username and Password not accepted.\n" \
                   "Ensure the credentials stored in env vars are set correct.\n" \
                   "Logon to https://myaccount.google.com/lesssecureapps and turn ON access to less secure apps.\n" \
                   "If 2 factor authentication is enabled, set `gmail_pass` to the generated App Password.\n" \
                   "More info: https://support.google.com/mail/?p=BadCredentials\n"
        except SMTPConnectError:
            return "Error during connection establishment with GMAIL server.\n"

        server.sendmail(
            from_addr=self.sender,
            to_addrs=[self.recipient],
            msg=self.multipart_message().as_string()
        )
        server.quit()

        return f'Client information has been emailed to {self.recipient}'
