import imaplib
import email
import os

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
                raw_email = data[0][1]
                decoded_raw_email = raw_email.decode('utf-8')
                email_message = email.message_from_string(decoded_raw_email)
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":  # ignore attachments/html
                        body = part.get_payload(decode=True)
                        sender = (original_email['From'] + '\n')
                        sub = (original_email['Subject'] + '\n')
                        msg = (body.decode('utf-8'))
                        print(msg)
