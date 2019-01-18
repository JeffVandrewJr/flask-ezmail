import blinker
from flask_ezmail.message import Message
from flask_ezmail.utils import sanitize_address, PY3, sanitize_addresses
import smtplib
import time

signals = blinker.Namespace()

email_dispatched = signals.signal("email-dispatched", doc="""
Signal sent when an email is dispatched. This signal will also be sent
in testing mode, even though the email will not actually be sent.
""")


class Connection(object):
    """Handles connection to host."""

    def __init__(self, mail):
        self.mail = mail

    def __enter__(self):
        if self.mail.suppress:
            self.host = None
        else:
            self.host = self.configure_host()

        self.num_emails = 0

        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.host:
            self.host.quit()

    def configure_host(self):
        if self.mail.use_ssl:
            host = smtplib.SMTP_SSL(self.mail.server, self.mail.port)
        else:
            host = smtplib.SMTP(self.mail.server, self.mail.port)
        if self.mail.debug is not None:
            host.set_debuglevel(int(self.mail.debug))
        else:
            host.set_debuglevel(int(False))
        if self.mail.use_tls:
            host.starttls()
        if self.mail.username and self.mail.password:
            host.login(self.mail.username, self.mail.password)

        return host

    def send(self, message, envelope_from=None):
        """Verifies and sends message.

        :param message: Message instance.
        :param envelope_from: Email address to be used in MAIL FROM command.
        """
        assert message.send_to, "No recipients have been added"

        assert message.sender, (
                "The message does not specify a sender and a default sender "
                "has not been configured")

        if message.has_bad_headers():
            raise BadHeaderError

        if message.date is None:
            message.date = time.time()

        if self.host:
            self.host.sendmail(sanitize_address(envelope_from or message.sender),
                               list(sanitize_addresses(message.send_to)),
                               message.as_bytes() if PY3 else message.as_string(),
                               message.mail_options,
                               message.rcpt_options)

        email_dispatched.send(message)

        self.num_emails += 1

        if self.num_emails == self.mail.max_emails:
            self.num_emails = 0
            if self.host:
                self.host.quit()
                self.host = self.configure_host()

    def send_message(self, *args, **kwargs):
        """Shortcut for send(msg).

        Takes same arguments as Message constructor.

        :versionadded: 0.3.5
        """

        self.send(Message(*args, **kwargs))


class BadHeaderError(Exception):
    pass
