import datetime
import logging
import os

import gmailconnector as gc

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s'))
logger.addHandler(handler)
if os.getenv('debug'):
    debug = True
    logger.setLevel(logging.DEBUG)
else:
    debug = False
    logger.setLevel(logging.INFO)

logger.info("RUNNING TESTS on version: %s with logger level: %s", gc.version, logging.getLevelName(logger.level))


def test_run_read_email():
    """Test run read emails."""
    logger.info("Test initiated on read email")
    reader = gc.ReadEmail(folder=gc.Folder.all)
    filter1 = gc.Condition.since(since=datetime.date(year=2010, month=5, day=1))
    filter2 = gc.Condition.subject(subject="Security Alert")
    filter3 = gc.Condition.text(text=reader.env.gmail_user)
    filter4 = gc.Category.not_deleted
    response = reader.instantiate(filters=(filter1, filter2, filter3, filter4))  # Apply multiple filters
    assert response.status <= 299, response.body
    for each_mail in reader.read_mail(messages=response.body, humanize_datetime=False):  # False to get datetime object
        logger.debug(each_mail.date_time.date())
        logger.debug("[%s] %s" % (each_mail.sender_email, each_mail.sender))
        logger.debug("[%s] - %s" % (each_mail.subject, each_mail.body))
    logger.info("Test successful on read email")


def test_run_send_email_tls():
    """Test run send email using TLS encryption."""
    logger.info("Test initiated on send email using TLS")
    sender = gc.SendEmail(encryption=gc.Encryption.TLS)
    auth_status = sender.authenticate
    assert auth_status.ok, auth_status.body
    response = sender.send_email(recipient=sender.env.recipient, sender="GmailConnector Tester",
                                 subject="GmailConnector Test Run - TLS - " + datetime.datetime.now().strftime('%c'))
    assert response.ok, response.body
    logger.info("Test successful on send email using TLS")


def test_run_send_email_ssl():
    """Test run send email using SSL encryption."""
    logger.info("Test initiated on send email using SSL")
    sender = gc.SendEmail(encryption=gc.Encryption.SSL)
    auth_status = sender.authenticate
    assert auth_status.ok, auth_status.body
    response = sender.send_email(recipient=sender.env.recipient, sender="GmailConnector Tester",
                                 subject="GmailConnector Test Run - SSL - " + datetime.datetime.now().strftime('%c'))
    assert response.ok, response.body
    logger.info("Test successful on send email using SSL")


def test_run_send_sms_tls():
    """Test run send sms using TLS encryption."""
    logger.info("Test initiated on send sms using TLS")
    sender = gc.SendSMS(encryption=gc.Encryption.TLS)
    auth_status = sender.authenticate
    assert auth_status.ok, auth_status.body
    response = sender.send_sms(subject="GmailConnector Test Run - TLS", delete_sent=True,
                               message=datetime.datetime.now().strftime('%c'))
    assert response.ok, response.body
    logger.info("Test successful on send sms using TLS")


def test_run_send_sms_ssl():
    """Test run send sms using SSL encryption."""
    logger.info("Test initiated on send sms using SSL")
    sender = gc.SendSMS(encryption=gc.Encryption.SSL)
    auth_status = sender.authenticate
    assert auth_status.ok, auth_status.body
    response = sender.send_sms(subject="GmailConnector Test Run - SSL", delete_sent=True,
                               message=datetime.datetime.now().strftime('%c'))
    assert response.ok, response.body
    logger.info("Test successful on send sms using SSL")


def test_run_validate_email_smtp_off():
    """Test run on email validator with SMTP disabled."""
    logger.info("Test initiated on email validator with SMTP disabled.")
    response = gc.validate_email(gc.EgressConfig().gmail_user, smtp_check=False, debug=debug, logger=logger)
    assert response.ok, response.body
    logger.info("Test successful on validate email with SMTP enabled.")


def test_run_validate_email_smtp_on():
    """Test run on email validator with SMTP enabled."""
    logger.info("Test initiated on email validator with SMTP enabled.")
    response = gc.validate_email(gc.IngressConfig().gmail_user, smtp_check=True, debug=debug, logger=logger)
    assert response.status <= 299, response.body
    logger.info("Test successful on validate email with SMTP disabled.")


if __name__ == '__main__':
    test_run_validate_email_smtp_off()
    test_run_validate_email_smtp_on()
    test_run_send_email_tls()
    test_run_send_email_ssl()
    test_run_send_sms_tls()
    test_run_send_sms_ssl()
    test_run_read_email()
