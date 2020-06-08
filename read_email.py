import imaplib
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
