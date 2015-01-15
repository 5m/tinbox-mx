import logging
from trakapi import Trak

_log = logging.getLogger(__name__)

trak = Trak()


def insert(mail):
    try:
        from_address = mail.get_envelope()['from']

        trak.create_ticket(from_address, mail.subject, mail.get_body_content())
    except Exception:
        _log.exception('Could not insert into trak.')
        raise

