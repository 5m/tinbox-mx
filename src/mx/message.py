from collections import namedtuple
from email import message_from_bytes
from email.headerregistry import Address, AddressHeader, SingleAddressHeader
from email.message import MIMEPart
from email.policy import default as email_policy
from email.utils import parseaddr
from functools import wraps

from .encoding import smart_decode


def parse(data):
    """
    Parse and decode raw message into MailMessage
    Takes raw message as bytes, and tries to clean it up into a decoded Message.

    :param data: Raw mail message bytes
    :return: MailMessage
    """
    return message_from_bytes(data, policy=email_policy, _class=MIMEMessage)


Attachment = namedtuple('Attachment', ('id', 'content_type', 'encoding', 'disposition', 'filename', 'data'))


def Header(name, attr=None, id=False):
    @wraps(MIMEPart.__getitem__)
    def wrapper(self):
        value = self[name]
        if value:
            if attr:
                value = getattr(value, attr)
            if id:
                _, value = parseaddr(value)
        return value
    return property(wrapper)


class MIMEMessage(MIMEPart):
    """
    Example:
    > message.message_id
    > message.subject
    > message.date

    > message.get_envelope()
    > message.get_body_content('html')
    > message.get_attachments()
    """

    # Header shortcuts
    uid = Header('message-id', id=True)
    message_id = uid
    content_id = Header('content-id', id=True)
    content_disposition = Header('content-disposition', attr='content_disposition')
    content_transfer_encoding = Header('content-transfer-encoding', attr='cte')
    subject = Header('subject')
    date = Header('date', attr='datetime')

    def __init__(self, policy=None):
        super(MIMEMessage, self).__init__(policy=policy)
        self.policy.content_manager.add_get_handler('text', self.__class__._decode_text_content)

    def _decode_text_content(self, *args, **kwargs):
        content = self.get_payload(decode=True)
        charset = self.get_param('charset', 'ASCII')
        return smart_decode(content, charset)

    def get_addresses(self, *headers):
        addresses = tuple()

        for header in headers:
            value = self[header]
            if value:
                if isinstance(value, AddressHeader):
                    addresses += value.addresses
                elif isinstance(value, SingleAddressHeader):
                    addresses += (value.address,)
                else:
                    # Probably UnstructuredHeader, cast to Address
                    addresses += (Address(addr_spec=value),)

        return addresses

    def get_envelope(self):
        return {
            'from': self.get_addresses('from', 'sender'),
            'to': self.get_addresses('to', 'delivered-to'),
        }

    def get_body_content(self, *preference):
        if not preference:
            preference = ('plain', 'html')
        body = self.get_body(preferencelist=preference)
        if body:
            return body.get_content()

    def get_attachments(self):
        for part in self.walk():
            for a in part.iter_attachments():
                yield a.as_attachment()

    def as_attachment(self):
        content_id = self.content_id or self['x-attachment-id']
        content_type = self.get_content_type()
        encoding = self.content_transfer_encoding
        disposition = self.content_disposition
        filename = self.get_filename()

        return Attachment(content_id, content_type, encoding, disposition, filename, self.get_content())
