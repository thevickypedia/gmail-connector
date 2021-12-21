[![Pypi-version](https://img.shields.io/pypi/v/gmail-connector)](https://pypi.org/project/gmail-connector)
[![Pypi-py-version](https://img.shields.io/pypi/pyversions/gmail-connector)](https://pypi.org/project/gmail-connector)

![docs](https://github.com/thevickypedia/gmail-connector/actions/workflows/docs.yml/badge.svg)
![pypi](https://github.com/thevickypedia/gmail-connector/actions/workflows/python-publish.yml/badge.svg)

[![Pypi-format](https://img.shields.io/pypi/format/gmail-connector)](https://pypi.org/project/gmail-connector/#files)
[![Pypi-status](https://img.shields.io/pypi/status/gmail-connector)](https://pypi.org/project/gmail-connector)

![Maintained](https://img.shields.io/maintenance/yes/2021)
[![GitHub Repo created](https://img.shields.io/date/1599432310)](https://api.github.com/repos/thevickypedia/gmail-connector)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/y/thevickypedia/gmail-connector)](https://api.github.com/repos/thevickypedia/gmail-connector)
[![GitHub last commit](https://img.shields.io/github/last-commit/thevickypedia/gmail-connector)](https://api.github.com/repos/thevickypedia/gmail-connector)

# Gmail Connector
Python module to, send SMS, emails and read `unread` emails in `inbox` folder.

###### Modules and Protocols
- `email` - Format emails as `MIMEMultipart` object, read emails from `bytes` and `str` and decode headers.
- `smtplib` - `SMTP` Simple Mail Transfer Protocol to connect to `gmail` server, do `auth` and perform outgoing tasks.
- `imaplib` - `IMAP` Internet Message Access Protocol to access messages in an email mailbox.

## Usage
`pip install gmail-connector`

<br>

[Send SMS](https://github.com/thevickypedia/gmail-connector/blob/master/gmailconnector/send_sms.py)
```python
from gmailconnector.send_sms import Messenger

response = Messenger(
    gmail_user='username@gmail.com',
    gmail_pass='<ACCOUNT_PASSWORD>',
    phone='+11234567890',
    message='Test SMS using gmail-connector'
).send_sms()
if response.ok:
    print(response.json())
```
<details>
<summary><strong>More on <a href="https://github.com/thevickypedia/gmail-connector/blob/master/gmailconnector/send_sms.py">Send SMS</a></strong></summary>

###### Additional args:
- **subject:** Subject of the message. Defaults to `Message from GmailConnector`
- **carrier:** Use any of ``at&t``, ``t-mobile``, ``verizon``, ``boost``, ``cricket``, ``us-cellular``. Defaults to `t-mobile`.
- **sms_gateway:** SMS gateway of the carrier. Defaults to ``tmomail.net`` since the default carrier is ``t-mobile``.
- **delete_sent:** Boolean flag to delete the outbound email from SentItems. Defaults to ``True``

> Note: If known, using the `sms_gateway` will ensure proper delivery of the SMS.
</details>

[Send Email](https://github.com/thevickypedia/gmail-connector/blob/master/gmailconnector/send_email.py)
```python
from gmailconnector.send_email import SendEmail

response = SendEmail(
        gmail_user='username@gmail.com',
        gmail_pass='<ACCOUNT_PASSWORD>',
        recipient='another_username@gmail.com',
        subject='Howdy!'
    ).send_email()
if response.ok:
    print(response.json())
```
<details>
<summary><strong>More on <a href="https://github.com/thevickypedia/gmail-connector/blob/master/gmailconnector/send_email.py">Send Email</a></strong></summary>

###### Additional args:
- **body:** Body of the email. Defaults to blank.
- **attachment:** Filename that has to be attached.
- **cc:** Email address of the recipient to whom the email has to be CC'd.
- **bcc:** Email address of the recipient to whom the email has to be BCC'd.

> Note: To send email to more than one recipient, wrap `recipient`/`cc`/`bcc` in a list.
>
> `recipient=['username1@gmail.com', 'username2@gmail.com']`
</details>

[Read Email](https://github.com/thevickypedia/gmail-connector/blob/master/gmailconnector/read_email.py)
```python
from gmailconnector.read_email import ReadEmail

ReadEmail(
    gmail_user='username@gmail.com',
    gmail_pass='<ACCOUNT_PASSWORD>'
).read_email()
```

### Linting
`PreCommit` will ensure linting, and the doc creation are run on every commit.

**Requirement**
<br>
`pip install --no-cache --upgrade sphinx pre-commit recommonmark`

**Usage**
<br>
`pre-commit run --all-files`

### Change Log
**Requirement**
`pip install --no-cache --upgrade changelog-generator`

**Usage**
`changelog`

### Pypi Module
[https://pypi.org/project/gmail-connector/](https://pypi.org/project/gmail-connector/)

### Runbook
[https://thevickypedia.github.io/gmail-connector/](https://thevickypedia.github.io/gmail-connector/)

### Repository
[https://github.com/thevickypedia/gmail-connector](https://github.com/thevickypedia/gmail-connector)

## License & copyright

&copy; Vignesh Sivanandha Rao, Gmail Connector

Licensed under the [MIT License](https://github.com/thevickypedia/gmail-connector/blob/master/LICENSE)
