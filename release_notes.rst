Release Notes
=============

v1.0.3 (11/24/2024)
-------------------
- Loosen `pydantic` version

v1.0.2 (06/05/2024)
-------------------
- Removes complexity with phone number validation
- Improved code readability

v1.0.1 (05/26/2024)
-------------------
- Includes a retry logic for occasional errors while sending emails
- Improved linting and updates to docs and dependencies

v1.0 (10/26/2023)
-----------------
- Uses ``pydantic`` for input validations
- Includes ``Enum`` wrappers around options
- Open access for SMS Gateway and Country codes
- Includes a bug fix for missing sender while reading emails
- Better documentation and runbook

v1.0b (10/26/2023)
------------------
- Release beta version for v1

v1.0a (10/26/2023)
------------------
- Prerelease for v1

0.9.1 (08/30/2023)
------------------
- Includes some minor modifications in type hinting

0.9 (05/01/2023)
----------------
- Support validating email addresses for iterables
- Update README.md and test_runner.py

0.8 (04/03/2023)
----------------
- Validate recipient address format in send_email.py
- Make validator available on name space package
- Update test runner

0.7 (04/03/2023)
----------------
- Make all objects available in __init__.py
- Unhook changelog dependency with version numbers
- Exclude private members in docs

0.7.6 (04/02/2023)
------------------
- Add more exception handlers
- Fix condition in delete sent for SMS

0.7.5 (04/02/2023)
------------------
- Remove unused namespace package
- Reformat imports and update README.md

0.6.9 (03/17/2023)
------------------
- Simplify samples in README.md and update responses
- Update pypi classifiers

0.6.8 (02/11/2023)
------------------
- Fix date filter bug on conditions
- Remove enum on object types
- Remove validation of folder argument

0.6.7 (02/09/2023)
------------------
- Update README.md

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

0.2.3 (08/11/2021)
------------------
- Add new lines to the message start to separate subject and body of the SMS
- Update sphinx documentation to 4.1.2

0.2.2 (08/02/2021)
------------------
- bump version

0.2.1 (07/24/2021)
------------------
- Remove logger module.
- Add exception handlers for Messenger class.
- Update docs and CHANGELOG
- Bump version.

0.2.0 (07/22/2021)
------------------
- Return a dictionary element after sending an email/SMS.
- Add status code and description to return dict.
- Update docs and CHANGELOG
- Bump version.

0.1.9 (07/19/2021)
------------------
- Allow users to add multiple recipients while sending email.
- Add CC and BCC options.
- Check if attachment file is available before trying to attach.
- Wrap recipient, cc and bcc items in a single list before email kick off.
- Remove sender arg and default to the user login email address.
- Fix version number format.

0.0.18 (07/19/2021)
-------------------
- 1. Add logging
- 2. Remove print statements
- 3. Bump version

0.0.17 (07/19/2021)
-------------------
- 1. Bump version to support github action
- 2. Auto upload to pypi

0.0.0 (07/19/2021)
------------------
- run on release

0.0.15 (07/19/2021)
-------------------
- 1. Onboard `pypi` module
- 2. Add `setup.py`, `setup.cfg`, `__init__.py`, `CHANGELOG`
- 3. Update README.md and docs
- 4. Move files to `gmailconnector` support package

0.0.16 (07/19/2021)
-------------------
- 1. Onboard `pypi` module
- 2. Add `setup.py`, `setup.cfg`, `__init__.py`, `CHANGELOG`
- 3. Update README.md and docs
- 4. Move files to `gmailconnector` support package
