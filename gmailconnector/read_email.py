from datetime import datetime, timedelta
from email import message_from_bytes, message_from_string
from email.header import decode_header, make_header
from imaplib import IMAP4_SSL


class ReadEmail:
    """Initiates Emailer object to authenticate and print the unread emails.

    >>> ReadEmail

    Args:
        - gmail_user: Email address (GMAIL)
        - gmail_pass: Login password

    """

    def __init__(self, gmail_user: str, gmail_pass: str):
        """Gathers all the necessary parameters to read emails."""
        self.mail = IMAP4_SSL('imap.gmail.com')  # connects to gmail using imaplib
        # noinspection PyBroadException
        try:
            self.mail.login(user=gmail_user, password=gmail_pass)  # login to your gmail account using the env variables
            self.mail.list()  # list all the folders within your mailbox (like inbox, sent, drafts, etc)
            self.mail.select('inbox')  # selects inbox from the list
        except Exception:
            self.mail = None
        self.username = gmail_user

    def __del__(self):
        """Destructor called to close the mailbox and logout."""
        if self.mail:
            self.mail.close()
            self.mail.logout()

    def main(self) -> tuple:
        """Prints the number of emails and gets user confirmation before proceeding, press N/n to quit.

        Returns:
            `tuple`:
            A tuple containing number of email messages, return code and the messages itself.

        """
        n = 0
        return_code, messages = self.mail.search(None, 'UNSEEN')  # looks for unread emails
        if return_code == 'OK':
            n = len(messages[0].split())
        else:
            exit("Unable access your email account.")
        if not n:
            exit(f'You have no unread emails. Account username: {self.username}')
        return n, return_code, messages

    def read_email(self) -> dict or None:
        """Prints unread emails one by one after getting user confirmation."""
        if not self.mail:
            return_msg = 'BUMMER! Unable to read your emails.\n\nTroubleshooting Steps:\n' \
                         '\t1. Make sure your username and password are correct.\n' \
                         '\t2. Logon to https://myaccount.google.com/lesssecureapps and turn ON less secure apps.\n' \
                         '\t3. If you have enabled 2 factor authentication, use thee App Password generated.'
            return {
                'ok': False,
                'status': 401,
                'body': return_msg
            }

        n, return_code, messages = self.main()
        user_ip = input(f'You have {n} unread emails. Press Y/y to continue:\n')
        if return_code != 'OK' or not (user_ip == 'Y' or user_ip == 'y'):  # proceeds only if user input is Y or y
            return

        i = 0
        for nm in messages[0].split():
            i += 1
            dummy, data = self.mail.fetch(nm, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    original_email = message_from_bytes(response_part[1])  # gets the rawest content
                    date = (original_email['Received'].split(';')[-1]).strip()  # gets raw received time
                    if '(PDT)' in date:
                        datetime_obj = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S -0700 (PDT)") + timedelta(hours=2)
                    elif '(PST)' in date:
                        datetime_obj = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S -0800 (PST)") + timedelta(hours=2)
                    else:
                        datetime_obj = datetime.now()
                    receive = (datetime_obj.strftime("on %A, %B %d, %Y at %I:%M %p CT"))  # formats datetime
                    # noinspection PyUnresolvedReferences
                    raw_email = data[0][1]
                    raw_email_string = raw_email.decode('utf-8')  # decodes the raw email
                    email_message = message_from_string(raw_email_string)  # extracts message from string
                    # generates the file names in a directory tree by walking the tree bottom-up
                    # it yields a 3-tuple (body, sender, subject).
                    for part in email_message.walk():
                        """The 'if' condition below is important as parts of an email may include
                        text/html, multipart/alternative, text/plain and other attachments.
                        We choose only text/plain as it is the only code-friendly part of a multipart email.
                        Choosing text/html can make the output look messed up with unnecessary html tags
                        Choosing multipart/alternative leaves us with decoding errors.
                        Though I have an exception handler to handle the decoding exceptions,
                        if the condition below is removed the loop will keep running through all the parts
                        within a single email"""
                        if part.get_content_type() == "text/plain":  # ignore attachments/html/multipart
                            # returns message's entire payload, a string or a message instance.
                            # decode=true decodes the payload received.
                            body = part.get_payload(decode=True)
                            # gets sender email and subject and removes unnecessary white spaces
                            sender = make_header(decode_header((original_email['From']).split(' <')[0]))
                            sub = make_header(decode_header(original_email['Subject'])) \
                                if original_email['Subject'] else None
                            print(f"You have an email from {sender} with subject '{sub}' {receive}")
                            #  gets user confirmation before printing the decoded body of the email
                            try:
                                msg = (body.decode('utf-8')).strip()  # decodes body of the email
                                get_user_input = input('Enter Y/N to read the email:\n')
                                if get_user_input == 'Y' or get_user_input == 'y':
                                    print(f'{msg}\n')
                            except (UnicodeDecodeError, AttributeError):  # catches both the decoding errors
                                continue
                            if i < n:  # proceeds only if loop count is less than the number of unread emails
                                continue_confirmation = input('Enter N/n to quit, any other key to continue:\n')
                                if continue_confirmation == 'N' or continue_confirmation == 'n':
                                    return


if __name__ == '__main__':
    from os import environ

    if response := ReadEmail(gmail_user=environ.get('gmail_user'), gmail_pass=environ.get('gmail_pass')).read_email():
        print(response.get('body'))
