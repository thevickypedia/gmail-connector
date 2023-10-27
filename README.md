[![Pypi-version](https://img.shields.io/pypi/v/gmail-connector)][pypi]
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)

[![](https://github.com/thevickypedia/gmail-connector/actions/workflows/pages/pages-build-deployment/badge.svg)][gha-pg]
[![pypi](https://github.com/thevickypedia/gmail-connector/actions/workflows/python-publish.yml/badge.svg)][gha-pypi]
[![none](https://github.com/thevickypedia/gmail-connector/actions/workflows/markdown-validation.yml/badge.svg)][gha-md]

[![Pypi-format](https://img.shields.io/pypi/format/gmail-connector)][pypi-files]
[![Pypi-status](https://img.shields.io/pypi/status/gmail-connector)][pypi]
[![dependents](https://img.shields.io/librariesio/dependents/pypi/gmail-connector)][dependants]

[![GitHub Repo created](https://img.shields.io/date/1599432310)][api-repo]
[![GitHub commit activity](https://img.shields.io/github/commit-activity/y/thevickypedia/gmail-connector)][api-repo]
[![GitHub last commit](https://img.shields.io/github/last-commit/thevickypedia/gmail-connector)][api-repo]

# Gmail Connector
Python module to send SMS, emails and read emails in any folder.

> As of May 30, 2022, Google no longer supports third party applications accessing Google accounts only using username 
> and password (which was originally available through [lesssecureapps](https://myaccount.google.com/lesssecureapps))
> <br>
> An alternate approach is to generate [apppasswords](https://myaccount.google.com/apppasswords) instead.<br>
> **Reference:** https://support.google.com/accounts/answer/6010255

## Installation
```shell
pip install gmail-connector
```

## Env Vars
Environment variables can be loaded from any `.env` file.
```bash
GMAIL_USER='username@gmail.com',
GMAIL_PASS='<ACCOUNT_PASSWORD>'
```

<details>
<summary><strong>Env variable customization</strong></summary>

To load a custom `.env` file, set the filename as the env var `env_file` before importing `gmailconnector`
```python
import os
os.environ['env_file'] = 'custom'  # to load a custom .env file
import gmailconnector as gc
```
To avoid using env variables, arguments can be loaded during object instantiation.
```python
import gmailconnector as gc
kwargs = dict(gmail_user='EMAIL_ADDRESS',
              gmail_pass='PASSWORD',
              encryption=gc.Encryption.SSL,
              timeout=5)
email_obj = gc.SendEmail(**kwargs)
```
</details>

## Usage
### [Send SMS][send-sms]
```python
import gmailconnector as gc

sms_object = gc.SendSMS()
# sms_object = gc.SendSMS(encryption=gc.Encryption.SSL) to use SSL
auth = sms_object.authenticate  # Authentication happens before sending SMS if not instantiated separately
assert auth.ok, auth.body
response = sms_object.send_sms(phone='1234567890', country_code='+1', message='Test SMS using gmail-connector',
                               sms_gateway=gc.SMSGateway.verizon, delete_sent=True)  # set as False to keep the SMS sent
assert response.ok, response.json()
print(response.body)
```
<details>
<summary><strong>
More on <a href="https://github.com/thevickypedia/gmail-connector/blob/main/gmailconnector/send_sms.py">Send SMS</a>
</strong></summary>

:warning: Gmail's SMS Gateway has a payload limit. So, it is recommended to break larger messages into multiple SMS.

###### Additional args:
- **subject:** Subject of the message. Defaults to `Message from email address`
- **sms_gateway:** SMS gateway of the carrier. Defaults to `tmomail.net`
- **delete_sent:** Boolean flag to delete the outbound email from SentItems. Defaults to `False`

> Note: If known, using the `sms_gateway` will ensure proper delivery of the SMS.
</details>

### [Send Email][send-email]
```python
import gmailconnector as gc

mail_object = gc.SendEmail()
# mail_object = gc.SendEmail(encryption=gc.Encryption.SSL) to use SSL
auth = mail_object.authenticate  # Authentication happens in send_email if not instantiated beforehand
assert auth.ok, auth.body

# Send a basic email
response = mail_object.send_email(recipient='username@gmail.com', subject='Howdy!')
assert response.ok, response.json()
print(response.body)
```

**To verify recipient email before sending. Authentication not required, uses SMTP port `25`**
```python
import gmailconnector as gc

validation_result = gc.validate_email(email_address='someone@example.com')
if validation_result.ok is True:
    print('valid')  # Validated and found the recipient address to be valid
elif validation_result.ok is False:
    print('invalid')  # Validated and found the recipient address to be invalid
else:
    print('validation incomplete')  # Couldn't validate (mostly because port 25 is blocked by ISP)
```

<details>
<summary><strong>
More on <a href="https://github.com/thevickypedia/gmail-connector/blob/main/gmailconnector/send_email.py">Send Email
</a></strong></summary>

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

### [Read Email][read-email]
```python
import datetime

import gmailconnector as gc

reader = gc.ReadEmail(folder=gc.Folder.all)
filter1 = gc.Condition.since(since=datetime.date(year=2010, month=5, day=1))
filter2 = gc.Condition.subject(subject="Security Alert")
filter3 = gc.Condition.text(reader.env.gmail_user)
filter4 = gc.Category.not_deleted
response = reader.instantiate(filters=(filter1, filter2, filter3, filter4))  # Apply multiple filters
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

### [Release Notes][release-notes]
**Requirement**
```shell
python -m pip install gitverse
```

**Usage**
```shell
gitverse-release reverse -f release_notes.rst -t 'Release Notes'
```

### Pypi Module
[![pypi-module](https://img.shields.io/badge/Software%20Repository-pypi-1f425f.svg)][packaging]

[https://pypi.org/project/gmail-connector/][pypi]

### Runbook
[![made-with-sphinx-doc](https://img.shields.io/badge/Code%20Docs-Sphinx-1f425f.svg)][sphinx]

[https://thevickypedia.github.io/gmail-connector/][runbook]

## License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License][license]

[api-repo]: https://api.github.com/repos/thevickypedia/gmail-connector
[read-email]: https://github.com/thevickypedia/gmail-connector/blob/main/gmailconnector/read_email.py
[send-email]: https://github.com/thevickypedia/gmail-connector/blob/main/gmailconnector/send_email.py
[send-sms]: https://github.com/thevickypedia/gmail-connector/blob/main/gmailconnector/send_sms.py
[release-notes]: https://github.com/thevickypedia/gmail-connector/blob/main/release_notes.rst
[license]: https://github.com/thevickypedia/gmail-connector/blob/main/LICENSE
[pypi]: https://pypi.org/project/gmail-connector/
[pypi-files]: https://pypi.org/project/gmail-connector/#files
[runbook]: https://thevickypedia.github.io/gmail-connector/
[packaging]: https://packaging.python.org/tutorials/packaging-projects/
[sphinx]: https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html
[gha-md]: https://github.com/thevickypedia/gmail-connector/actions/workflows/markdown-validation.yml
[gha-pg]: https://github.com/thevickypedia/gmail-connector/actions/workflows/pages/pages-build-deployment
[gha-pypi]: https://github.com/thevickypedia/gmail-connector/actions/workflows/python-publish.yml
[dependants]: https://github.com/thevickypedia/gmail-connector/network/dependents
