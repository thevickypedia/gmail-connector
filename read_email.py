import email
import imaplib
import os
from datetime import datetime, timedelta

u = os.getenv('user')
p = os.getenv('pass')

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(u, p)
mail.list()
mail.select('inbox')

return_code, messages = mail.search(None, '(UNSEEN)')
if return_code == 'OK':
    for num in messages[0].split():
        typ, data = mail.fetch(num, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                original_email = email.message_from_bytes(response_part[1])
                raw_receive = (original_email['Received'].split(';')[-1]).strip()
                received_pdt = (raw_receive.split(',')[-1].split('-')[0]).strip()
                datetime_obj = datetime.strptime(received_pdt, "%d %b %Y %H:%M:%S") + timedelta(hours=2)
                receive = (datetime_obj.strftime("on %A, %B %d, %Y at %I:%M %p CDT"))
                raw_email = data[0][1]
                raw_email_string = raw_email.decode('utf-8')
                email_message = email.message_from_string(raw_email_string)
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":  # ignore attachments/html
                        body = part.get_payload(decode=True)
                        sender = (original_email['From'] + '\n').strip()
                        sub = (original_email['Subject'] + '\n').strip()
                        msg = (body.decode('utf-8')).strip()
                        print(f"You have an email from {sender} with subject '{sub}' {receive}")
                        get_user_input = input('Enter Y/N to read the email:\n')
                        if get_user_input == 'Y' or get_user_input == 'y':
                            print(f'{msg}\n')
                        else:
                            print(f'We respect your privacy, body of the email from {sender} '
                                  'will not be displayed.\n')
