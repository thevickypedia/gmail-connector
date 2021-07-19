# Gmail Connector

## Pypi Module
https://pypi.org/project/gmail-connector/

### Usage
`pip install gmail-connector`

<br>

[Send SMS](https://github.com/thevickypedia/gmail-connector/blob/master/send_sms.py)

```python
from os import environ
from gmailconnector.send_sms import Messenger

# noinspection PyTypeChecker
messenger = Messenger(
    gmail_user=environ.get('gmail_user'),
    gmail_pass=environ.get('gmail_pass'),
    phone_number=environ.get('phone'),
    message='Test SMS using gmail-connector'
)
print(messenger.send_sms())
```

[Send Email](https://github.com/thevickypedia/gmail-connector/blob/master/send_email.py)
```python
from os import environ
from pathlib import PurePath
from gmailconnector.send_email import SendEmail

email_obj = SendEmail(
        gmail_user=environ.get('gmail_user'),
        gmail_pass=environ.get('gmail_pass'),
        recipient=environ.get('recipient'),
        subject='Howdy!',
        attachment=PurePath(__file__).name,
        body='Attached is the code that generated this very email',
        sender=None
    )
print(email_obj.send_email())
```

[Read Email](https://github.com/thevickypedia/gmail-connector/blob/master/read_email.py)
```python
from os import environ
from gmailconnector.read_email import ReadEmail

ReadEmail(
    gmail_user=environ.get('gmail_user'),
    gmail_pass=environ.get('gmail_pass')
).read_email()
```

### Pre-Commit
Install `pre-commit` to run `flake8` and `isort` for linting and `sphinx` for documentation generator.

`pip3 install pre-commit==2.13.0 Sphinx==4.1.1`

`pre-commit run --all-files`

### Runbook
https://thevickypedia.github.io/gmail-connector/

## License & copyright

&copy; Vignesh Sivanandha Rao, Gmail Connector

Licensed under the [MIT License](https://github.com/thevickypedia/gmail-connector/blob/master/LICENSE)
