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
            print(response_part)
            if isinstance(response_part, tuple):
                original = email.message_from_bytes(response_part[1])
                raw_email = data[0][1]
                raw_email_string = raw_email.decode('utf-8')
                email_message = email.message_from_string(raw_email_string)
                print(email_message)
