import re
import logging

from tinbox_client import Tinbox

from .errors import BackendError

_log = logging.getLogger(__name__)

tinbox = Tinbox()


def insert(mail):
    try:
        envelope = mail.get_envelope()
        email, name = envelope['from']

        body_content = mail.get_body_content()

        attachments = list(mail.get_attachments())

        uuids = []

        for match in re.finditer(r'[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}',
                                 body_content):
            uuids.append(match.group(0))

        resp = tinbox.create_ticket(
            email, mail.subject, mail.get_body_content(),
            sender_name=name, context=uuids or None,
            attachments=[a.filename for a in attachments])

        for attachment_pk, attachment in zip(resp['attachments'], attachments):
            tinbox.upload_attachment(attachment_pk, attachment.data)

    except Exception as e:
        _log.exception('Could not insert into tinbox.')
        raise BackendError(e)
