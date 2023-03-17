[![Pypi-version](https://img.shields.io/pypi/v/gmail-connector)](https://pypi.org/project/gmail-connector)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)

[![pages-build-deployment](https://github.com/thevickypedia/gmail-connector/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/thevickypedia/gmail-connector/actions/workflows/pages/pages-build-deployment)
[![pypi-publish](https://github.com/thevickypedia/gmail-connector/actions/workflows/python-publish.yml/badge.svg)](https://github.com/thevickypedia/gmail-connector/actions/workflows/python-publish.yml)

[![Pypi-format](https://img.shields.io/pypi/format/gmail-connector)](https://pypi.org/project/gmail-connector/#files)
[![Pypi-status](https://img.shields.io/pypi/status/gmail-connector)](https://pypi.org/project/gmail-connector)
[![dependents](https://img.shields.io/librariesio/dependents/pypi/gmail-connector)](https://github.com/thevickypedia/gmail-connector/network/dependents)

[![GitHub Repo created](https://img.shields.io/date/1599432310)](https://api.github.com/repos/thevickypedia/gmail-connector)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/y/thevickypedia/gmail-connector)](https://api.github.com/repos/thevickypedia/gmail-connector)
[![GitHub last commit](https://img.shields.io/github/last-commit/thevickypedia/gmail-connector)](https://api.github.com/repos/thevickypedia/gmail-connector)

# Gmail Connector
Python module to send SMS, emails and read emails in any folder.

> As of May 30, 2022, Google no longer supports third party applications accessing Google accounts only using username and password (which was originally available through [lesssecureapps](https://myaccount.google.com/lesssecureapps))<br>
> An alternate approach is to generate [apppasswords](https://myaccount.google.com/apppasswords) instead.<br>
> **Reference:** https://support.google.com/accounts/answer/6010255

## Installation
```shell
pip install gmail-connector
```

## Env Vars
Environment variables can be loaded from a `.env` file.
```bash
# For authentication
GMAIL_USER='username@gmail.com',
GMAIL_PASS='<ACCOUNT_PASSWORD>'

# For outbound emails
RECIPIENT='username@gmail.com'

# For outbound SMS
PHONE='1234567890'
```

### [Send SMS](https://github.com/thevickypedia/gmail-connector/blob/master/gmailconnector/send_sms.py)
```python
import gmailconnector as gc

sms_object = gc.SendSMS()
auth = sms_object.authenticate  # Authentication happens before sending SMS if not instantiated separately
assert auth.ok, auth.body
response = sms_object.send_sms(phone='+11234567890', message='Test SMS using gmail-connector',
                               carrier='verizon', delete_sent=False)  # Stores the SMS in email's sent items
assert response.ok, response.json()
print(response.body)
```
<details>
<summary><strong>More on <a href="https://github.com/thevickypedia/gmail-connector/blob/master/gmailconnector/send_sms.py">Send SMS</a></strong></summary>

:warning: Gmail's SMS Gateway has a payload limit. So, it is recommended to break larger messages into multiple SMS.

###### Additional args:
- **subject:** Subject of the message. Defaults to `Message from GmailConnector`
- **carrier:** Use any of ``at&t``, ``t-mobile``, ``verizon``, ``boost``, ``cricket``, ``us-cellular``. Defaults to `t-mobile`.
- **sms_gateway:** SMS gateway of the carrier. Defaults to ``tmomail.net`` since the default carrier is ``t-mobile``.
- **delete_sent:** Boolean flag to delete the outbound email from SentItems. Defaults to ``True``

> Note: If known, using the `sms_gateway` will ensure proper delivery of the SMS.
</details>

### [Send Email](https://github.com/thevickypedia/gmail-connector/blob/master/gmailconnector/send_email.py)
```python
import gmailconnector as gc

mail_object = gc.SendEmail()
auth = mail_object.authenticate  # Authentication happens in send_email if not instantiated beforehand
assert auth.ok, auth.body

# Send a basic email
response = mail_object.send_email(recipient='username@gmail.com', subject='Howdy!')
assert response.ok, response.json()
print(response.body)
```

**To verify recipient email before sending. Authentication not required, uses SMTP port `25`**
```python
from gmailconnector import validator

email_addr = 'someone@example.com'
validation_result = validator.validate_email(email_address=email_addr)
if validation_result.ok is True:
    print('valid')  # Validated and found the recipient address to be valid
elif validation_result.ok is False:
    print('invalid')  # Validated and found the recipient address to be invalid
else:
    print('validation incomplete')  # Couldn't validate (mostly because port 25 is blocked by ISP)
```

<details>
<summary><strong>More on <a href="https://github.com/thevickypedia/gmail-connector/blob/master/gmailconnector/send_email.py">Send Email</a></strong></summary>

```python
import os
import gmailconnector as gc

mail_object = gc.SendEmail()
auth = mail_object.authenticate  # Authentication happens in send_email if not instantiated beforehand
assert auth.ok, auth.body

# Different use cases to add attachments with/without custom filenames to an email
images = [os.path.join(os.getcwd(), 'images', image) for image in os.listdir('images')]
names = ['Apple', 'Flower', 'Balloon']

# Use case 1 - Send an email with attachments but no custom attachment name
response = mail_object.send_email(recipient='username@gmail.com', subject='Howdy!',
                                  attachment=images)
assert response.ok, response.body
print(response.json())

# Use case 2 - Use a dictionary of attachments and custom attachment names
response = mail_object.send_email(recipient='username@gmail.com', subject='Howdy!',
                                  custom_attachment=dict(zip(images, names)))
assert response.ok, response.body
print(response.json())

# Use case 3 - Use list of attachments and list of custom attachment names
response = mail_object.send_email(recipient='username@gmail.com', subject='Howdy!',
                                  attachment=[images], filename=[names])
assert response.ok, response.body
print(response.json())

# Use case 4 - Use a single attachment and a custom attachment name for it
response = mail_object.send_email(recipient='username@gmail.com', subject='Howdy!',
                                  attachment=os.path.join('images', 'random_apple_xroamutiypa.jpeg'), filename='Apple')
assert response.ok, response.body
print(response.json())
```

###### Additional args:
- **body:** Body of the email. Defaults to blank.
- **html_body:** Body of the email formatted as HTML. Supports inline images with a public `src`.
- **attachment:** Filename(s) that has to be attached.
- **filename:** Custom name(s) for the attachment(s). Defaults to the attachment name itself.
- **sender:** Name that has to be used in the email.
- **cc:** Email address of the recipient to whom the email has to be CC'd.
- **bcc:** Email address of the recipient to whom the email has to be BCC'd.

> Note: To send email to more than one recipient, wrap `recipient`/`cc`/`bcc` in a list.
>
> `recipient=['username1@gmail.com', 'username2@gmail.com']`
</details>

### [Read Email](https://github.com/thevickypedia/gmail-connector/blob/master/gmailconnector/read_email.py)
```python
import datetime

import gmailconnector as gc

reader = gc.ReadEmail(folder=gc.Folder.all)
filter1 = gc.Condition.since(since=datetime.date(year=2010, month=5, day=1))
filter2 = gc.Condition.subject(subject="Security Alert")
filter3 = gc.Category.not_deleted
response = reader.instantiate(filters=(filter1, filter2, filter3))  # Apply multiple filters at the same time
assert response.ok, response.body
for each_mail in reader.read_mail(messages=response.body, humanize_datetime=False):  # False to get datetime object
    print(each_mail.date_time.date())
    print("[%s] %s" % (each_mail.sender_email, each_mail.sender))
    print("[%s] - %s" % (each_mail.subject, each_mail.body))
```

### Linting
`PreCommit` will ensure linting, and the doc creation are run on every commit.

**Requirement**
```shell
pip install sphinx==5.1.1 pre-commit==2.20.0 recommonmark==0.7.1
```

**Usage**
```shell
pre-commit run --all-files
```

### Change Log
**Requirement**
```shell
pip install changelog-generator
```

**Usage**
```shell
changelog reverse -f release_notes.rst -t 'Release Notes'
```

### Pypi Module
[https://pypi.org/project/gmail-connector/](https://pypi.org/project/gmail-connector/)

### Runbook
[https://thevickypedia.github.io/gmail-connector/](https://thevickypedia.github.io/gmail-connector/)

### Repository
[https://github.com/thevickypedia/gmail-connector](https://github.com/thevickypedia/gmail-connector)

## License & copyright

&copy; Vignesh Sivanandha Rao

Licensed under the [MIT License](https://github.com/thevickypedia/gmail-connector/blob/master/LICENSE)
