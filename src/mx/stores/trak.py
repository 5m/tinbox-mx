from functools import lru_cache
import json
import logging
import os
from oauthlib.oauth2.rfc6749.clients.backend_application import \
    BackendApplicationClient
from requests_oauthlib.oauth2_session import OAuth2Session

_log = logging.getLogger(__name__)


class Settings:
    """
    Settings class for trak, handles loading and validation of settings.

    Uses self.__dict__ to store settings, providing instance-variable access
    to the settings. e.g. ``settings.client_id  # returns client id``.
    """
    required = ['base_url', 'client_id', 'client_secret', 'scope']

    def __init__(self, settings_dict):
        missing = []

        for key in self.required:
            if key not in settings_dict:
                missing.append(key)

        if missing:
            raise ValueError('The field(s) %r are missing from your trak '
                             'settings file.' % missing)

        self.__dict__ = settings_dict

    def get_url(self, path):
        return self.base_url + path

    @classmethod
    def from_file(cls, filename):
        return cls(json.load(open(filename, 'r')))



@lru_cache(maxsize=1)  # Cache the result of get_settings
def get_settings():
    settings_file = os.environ.get('TRAK_SETTINGS')

    if settings_file is None:
        raise ValueError('TRAK_SETTINGS missing from environment, can\'t '
                         'initialize.')

    return Settings.from_file(settings_file)


def get_client():
    """
    Handles OAuth2 authentication.
    :return: A requests-oauthlib OAuth2Session.
    """
    settings = get_settings()

    trak = OAuth2Session(
        client_id=settings.client_id,
        client=BackendApplicationClient(settings.client_id)
    )

    trak.fetch_token(settings.get_url('oauth2/token/'),
                     client_id=settings.client_id,
                     client_secret=settings.client_secret,
                     scope=settings.scope)

    return trak


def insert(mail):
    try:
        settings = get_settings()
        trak = get_client()

        from_address = mail.get_envelope()['from']

        trak.post(settings.get_url('tickets/'),
                  data={'sender_email': from_address,
                        'subject': mail.subject,
                        'body': mail.get_body_content()})
    except Exception:
        _log.exception('Could not insert into trak.')
        raise

