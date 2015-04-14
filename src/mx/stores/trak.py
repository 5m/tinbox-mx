import re
import logging

from trak_client import Trak

from .errors import BackendError

_log = logging.getLogger(__name__)

trak = Trak()


def insert(mail):
    try:
        envelope = mail.get_envelope()
        email, name = envelope['from']

        body_content = mail.get_body_content()

        uuids = []

        for match in re.finditer(r'[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}',
                                 body_content):
            uuids.append(match.group(0))

        trak.create_ticket(email, mail.subject, mail.get_body_content(),
                           sender_name=name,
                           context=uuids or None)

    except Exception as e:
        _log.exception('Could not insert into trak.')
        raise BackendError(e)

