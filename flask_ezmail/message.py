from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from flask_ezmail.utils import sanitize_address, sanitize_subject, force_text,\
        sanitize_addresses, message_policy, _has_newline, PY3, PY34
import re
import unicodedata


class Attachment(object):
    """Encapsulates file attachment information.

    :versionadded: 0.3.5

    :param filename: filename of attachment
    :param content_type: file mimetype
    :param data: the raw file data
    :param disposition: content-disposition (if any)
    """

    def __init__(self, filename=None, content_type=None, data=None,
                 disposition=None, headers=None):
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.disposition = disposition or 'attachment'
        self.headers = headers or {}


class Message(object):
    """Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param alts: A dict or an iterable to go through dict() that contains
        multipart alternatives
    :param sender: email sender address, or **MAIL_DEFAULT_SENDER** by default
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances
    :param reply_to: reply-to address
    :param date: send date
    :param charset: message character set
    :param extra_headers: A dictionary of additional headers for the message
    :param mail_options: A list of ESMTP options to be used in MAIL FROM
        command
    :param rcpt_options:  A list of ESMTP options to be used in RCPT commands
    """

    def __init__(self, subject='',
                 recipients=None,
                 body=None,
                 html=None,
                 alts=None,
                 sender=None,
                 cc=None,
                 bcc=None,
                 attachments=None,
                 reply_to=None,
                 date=None,
                 charset=None,
                 extra_headers=None,
                 mail_options=None,
                 rcpt_options=None,
                 ascii_attachments=False,):

        sender = sender

        if isinstance(sender, tuple):
            sender = "%s <%s>" % sender

        self.recipients = recipients or []
        self.subject = subject
        self.sender = sender
        self.reply_to = reply_to
        self.cc = cc or []
        self.bcc = bcc or []
        self.body = body
        self.alts = dict(alts or {})
        self.html = html
        self.date = date
        self.msgId = make_msgid()
        self.charset = charset
        self.extra_headers = extra_headers
        self.mail_options = mail_options or []
        self.rcpt_options = rcpt_options or []
        self.attachments = attachments or []
        self.ascii_attachments = ascii_attachments

    @property
    def send_to(self):
        return set(self.recipients) | set(self.bcc or ()) | set(self.cc or ())

    @property
    def html(self):
        return self.alts.get('html')

    @html.setter
    def html(self, value):
        if value is None:
            self.alts.pop('html', None)
        else:
            self.alts['html'] = value

    def _mimetext(self, text, subtype='plain'):
        """Creates a MIMEText object with the given subtype (default: 'plain')
        If the text is unicode, the utf-8 charset is used.
        """
        charset = self.charset or 'utf-8'
        return MIMEText(text, _subtype=subtype, _charset=charset)

    def _message(self):
        """Creates the email"""
        ascii_attachments = self.ascii_attachments
        encoding = self.charset or 'utf-8'

        attachments = self.attachments or []

        if len(attachments) == 0 and not self.alts:
            # No html content and zero attachments means plain text
            msg = self._mimetext(self.body)
        elif len(attachments) > 0 and not self.alts:
            # No html and at least one attachment means multipart
            msg = MIMEMultipart()
            msg.attach(self._mimetext(self.body))
        else:
            # Anything else
            msg = MIMEMultipart()
            alternative = MIMEMultipart('alternative')
            alternative.attach(self._mimetext(self.body, 'plain'))
            for mimetype, content in self.alts.items():
                alternative.attach(self._mimetext(content, mimetype))
            msg.attach(alternative)

        if self.subject:
            msg['Subject'] = sanitize_subject(
                force_text(self.subject), encoding
            )

        msg['From'] = sanitize_address(self.sender, encoding)
        msg['To'] = ', '.join(list(set(
            sanitize_addresses(self.recipients, encoding))))

        msg['Date'] = formatdate(self.date, localtime=True)
        # see RFC 5322 section 3.6.4.
        msg['Message-ID'] = self.msgId

        if self.cc:
            msg['Cc'] = ', '.join(list(set(sanitize_addresses(
                self.cc, encoding))))

        if self.reply_to:
            msg['Reply-To'] = sanitize_address(self.reply_to, encoding)

        if self.extra_headers:
            for k, v in self.extra_headers.items():
                msg[k] = v

        SPACES = re.compile(r'[\s]+', re.UNICODE)
        for attachment in attachments:
            f = MIMEBase(*attachment.content_type.split('/'))
            f.set_payload(attachment.data)
            encode_base64(f)

            filename = attachment.filename
            if filename and ascii_attachments:
                # force filename to ascii
                filename = unicodedata.normalize('NFKD', filename)
                filename = filename.encode('ascii', 'ignore').decode('ascii')
                filename = SPACES.sub(u' ', filename).strip()

            try:
                filename and filename.encode('ascii')
            except UnicodeEncodeError:
                if not PY3:
                    filename = filename.encode('utf8')
                filename = ('UTF8', '', filename)

            f.add_header('Content-Disposition',
                         attachment.disposition,
                         filename=filename)

            for key, value in attachment.headers.items():
                f.add_header(key, value)

            msg.attach(f)
        if message_policy:
            msg.policy = message_policy

        return msg

    def as_string(self):
        return self._message().as_string()

    def as_bytes(self):
        if PY34:
            return self._message().as_bytes()
        else:  # fallback for old Python (3) versions
            return self._message().as_string().encode(self.charset or 'utf-8')

    def __str__(self):
        return self.as_string()

    def __bytes__(self):
        return self.as_bytes()

    def has_bad_headers(self):
        """Checks for bad headers i.e. newlines in subject, sender or recipients.
        RFC5322: Allows multiline CRLF with trailing whitespace (FWS) in header
        """

        headers = [self.sender, self.reply_to] + self.recipients
        for header in headers:
            if _has_newline(header):
                return True

        if self.subject:
            if _has_newline(self.subject):
                for linenum, line in enumerate(self.subject.split('\r\n')):
                    if not line:
                        return True
                    if linenum > 0 and line[0] not in '\t ':
                        return True
                    if _has_newline(line):
                        return True
                    if len(line.strip()) == 0:
                        return True
        return False

    def is_bad_headers(self):
        from warnings import warn
        msg = '''is_bad_headers is deprecated, use the new
        has_bad_headers method instead.'''
        warn(DeprecationWarning(msg), stacklevel=1)
        return self.has_bad_headers()

    def send(self, connection):
        """Verifies and sends the message."""

        connection.send(self)

    def add_recipient(self, recipient):
        """Adds another recipient to the message.

        :param recipient: email address of recipient.
        """

        self.recipients.append(recipient)

    def attach(self,
               filename=None,
               content_type=None,
               data=None,
               disposition=None,
               headers=None):
        """Adds an attachment to the message.

        :param filename: filename of attachment
        :param content_type: file mimetype
        :param data: the raw file data
        :param disposition: content-disposition (if any)
        """
        self.attachments.append(
            Attachment(filename, content_type, data, disposition, headers))
