import logging
from trakapi import Trak

_log = logging.getLogger(__name__)

trak = Trak()


def insert(mail):
    try:
        envelope = mail.get_envelope()
        email, name = envelope['from']

        trak.create_ticket(email, mail.subject, mail.get_body_content(),
                           sender_name=name)
    except Exception:
        _log.exception('Could not insert into trak.')
        raise

