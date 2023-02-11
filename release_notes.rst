Release Notes
=============

0.6.8 (02/11/2023)
------------------
- Fix date filter bug on conditions
- Remove enum on object types
- Remove validation of folder argument

0.6.7 (02/09/2023)
------------------
- Update README.md

0.6.6 (02/09/2023)
------------------
- Add a feature to get body of the email when reading
- Add a feature to inject multiple filters when reading
- Convert response from read email as an object
- Change Messenger to SendSMS to keep it consistent
- Convert build to pyrpoject.toml and update README.md

0.6.5 (01/12/2023)
------------------
- Add more insight `custom_attachment` type hinting
- Update docstring

0.6.4 (01/08/2023)
------------------
- Change type hint from `object` to type method to support docker

0.6.3 (01/08/2023)
------------------
- Raise `ValueError`s when `recipient` or `phone` arg is missing
- Update README.md

0.6.2 (01/05/2023)
------------------
- Classify `UnresponsiveMailServer` is invalid destination

0.6.1 (01/05/2023)
------------------
- Catch edge case scenario in validation emails
- CHANGELOG -> release_notes.rst
- Update setup.py and README.md

0.6.0 (12/13/2022)
------------------
- Fix deleting sent sms from sent mail
- Block active process until completion
- Simplify responder.py

0.5.9 (12/08/2022)
------------------
- Add a flag to make smtp check optional
- Upgrade sphinx

0.5.8 (11/15/2022)
------------------
- Remove OS restriction to get MX records
- Remove unreliable port number access check
- Switch python publish to run on release
- Update README.md

0.5.7 (10/30/2022)
------------------
- Include package data to upload validators to pypi

0.5.6 (10/30/2022)
------------------
- Improve email validation
- Create a dedicated dir based module for it
- Update README.md and requirements

0.5.5 (10/29/2022)
------------------
- Feature improvements on send_email.py
- Add a feature to support multiple attachments in an email
- Create an arg to fail email if attachment fails
- Create a module to validate email using SMTP port
- Add usage examples in README.md

0.5.4 (10/21/2022)
------------------
- Instantiate the object before sending SMS or email
- Add an authenticate property
- Update README.md and docstrings

0.5.3 (10/08/2022)
------------------
- Add an option to format email body as HTML
- Fix a bug when calling thread to delete sent email after sms
- Fix a bug in sphinx doc creation
- Update docstrings

0.5.2 (06/08/2022)
------------------
- Remove verbose and override flags when loading .env

0.5.1 (02/21/2022)
------------------
- Update version compatibility in README.md
- Import local modules from __init__
- Add a script to build locally
- Remove docs from actions

0.5.0 (02/19/2022)
------------------
- Add a warning if count is called outside ReadEmail
- Strip string converted email info in the yielded dict

0.4.9 (02/19/2022)
------------------
- Read mails in all folders with different status
- Convert email receive time into local timezone
- Remove print statements and use yield instead
- Yield email information as a dictionary
- Upload to pypi when committed to master
- Update docs, README.md and CHANGELOG

0.4.8 (01/12/2022)
------------------
- Take a custom filename for the attachment
- Default to attachment name without the path
- Remove unnecessary variables

0.4.7 (01/09/2022)
------------------
- Check for `phone` and `recipient` in env var
- Take gmail username instead of email address

0.4.6 (01/08/2022)
------------------
- Load env vars from a .env file
- Reformat docstrings
- Fix sent item after sending an SMS

0.4.5 (01/01/2022)
------------------
- Add SMTP port number to send email

0.4.4 (12/30/2021)
------------------
- Add more information to payload restriction

0.4.3 (12/30/2021)
------------------
- Add payload limit for SMS

0.4.2 (12/22/2021)
------------------
- Remove endpoint validator due to high inaccuracies

0.4.1 (12/22/2021)
------------------
- Mark internal methods as private
- Include private methods in sphinx docs

0.4.0 (12/22/2021)
------------------
- Fix phone number digit validation

0.3.9 (12/20/2021)
------------------
- Create a separate method to validate input arguments
- Change arg phone_number to phone

0.3.8 (12/20/2021)
------------------
- Fix import issues with module vs sphinx

0.3.7 (12/20/2021)
------------------
- Specify carrier based sms-gateway to increase success rate
- Introduce carrier, sms_gateway and delete_sent as optional arguments
- Use a third-party email-validator to check endpoint before sending the email
- Remove redundant variables
- Add requirements.txt, update README.md and .gitignore

0.3.6 (11/10/2021)
------------------
- Return responses as a class object instead of a dictionary
- Delete messages after sending an SMS
- Do not remove docs directory if version is not bumped
- Generate CHANGELOG in reverse

0.3.5 (10/16/2021)
------------------
- Add project URLs and package requirements to pypi
- Add markdown support to sphinx autodocs
- Add a condition check for version upgrade
- Update docs and changelog

0.3.4 (08/11/2021)
------------------
- Add new lines to the message start to separate subject and body of the SMS
- Update sphinx documentation to 4.1.2

0.3.3 (08/04/2021)
------------------
- Fix incorrect HTTP return codes

0.3.2 (07/24/2021)
------------------
- Remove logger module.
- Add exception handlers for Messenger class.
- Update docs and CHANGELOG
- Bump version.

0.3.1 (07/22/2021)
------------------
- Return a dictionary element after sending an email/SMS.
- Add status code and description to return dict.
- Update docs and CHANGELOG
- Bump version.

0.3.0 (07/19/2021)
------------------
- Allow users to add multiple recipients while sending email.
- Add CC and BCC options.
- Check if attachment file is available before trying to attach.
- Wrap recipient, cc and bcc items in a single list before email kick off.
- Remove sender arg and default to the user login email address.
- Fix version number format.

0.2.9 (07/19/2021)
------------------
- Add logging
- Remove print statements
- Bump version

0.2.8 (07/19/2021)
------------------
- Bump version to support github action
- Auto upload to pypi

0.2.7 (07/19/2021)
------------------
- auto upload to pypi when tagged a release version

0.2.6 (07/19/2021)
------------------
- onboard docs.yml but only prints a statement

0.2.5 (07/19/2021)
------------------
- Add badges
- Update README.md and CHANGELOG
- Bump version

0.2.4 (07/18/2021)
------------------
- Onboard `pypi` module
- Add `setup.py`, `setup.cfg`, `__init__.py`, `CHANGELOG`
- Update README.md and docs
- Move files to `gmailconnector` support package

0.2.3 (07/18/2021)
------------------
- Increase page width and update README.md

0.2.2 (07/18/2021)
------------------
- Onboard send_sms.py and update docs

0.2.1 (07/17/2021)
------------------
- Onboard sphinx auto generated documentation

0.2.0 (07/17/2021)
------------------
- Refactor read_email.py and add send_email.py
- Add pre-commit for linting
- Update README.md

0.1.9 (06/28/2020)
------------------
- update README.md

0.1.8 (06/28/2020)
------------------
- add LICENSE

0.1.7 (06/28/2020)
------------------
- look for env variables before failing

0.1.6 (06/27/2020)
------------------
- included exception handler

0.1.5 (06/27/2020)
------------------
- modify date time type standards instead of using index values

0.1.4 (06/11/2020)
------------------
- fix typo

0.1.3 (06/09/2020)
------------------
- improve coding standards

0.1.2 (06/08/2020)
------------------
- improve coding standards

0.1.1 (06/08/2020)
------------------
- added comments

0.1.0 (06/08/2020)
------------------
- get user input before reading multiple emails

0.0.9 (06/08/2020)
------------------
- get user input before showing any content

0.0.8 (06/08/2020)
------------------
- include number of unread emails on top

0.0.7 (06/08/2020)
------------------
- user input condition to read email

0.0.6 (06/08/2020)
------------------
- pdt to cdt

0.0.5 (06/08/2020)
------------------
- added time when the email was received

0.0.4 (06/08/2020)
------------------
- decode body of the email and display only text part

0.0.3 (06/08/2020)
------------------
- decode raw email using email library

0.0.2 (06/08/2020)
------------------
- read raw email

0.0.1 (06/07/2020)
------------------
- Initial commit
