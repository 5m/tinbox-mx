import chardet


class EncodingError(Exception):
    pass


def smart_decode(data, charset):
    """
    Decodes data in given charset.
    On failure, guess charset and retry.
    """
    try:
        if isinstance(data, str):
            # It's already unicode so just return it
            return data
        else:
            return data.decode(charset, errors='strict')

    except UnicodeDecodeError:  # PY3
        # Looks like the charset lies, try to detect it
        return guess_encoding_and_decode(data, claimed=charset)

    except LookupError:
        # They gave us a crap encoding
        return guess_encoding_and_decode(data, claimed=charset)


def guess_encoding_and_decode(data, claimed=None, errors='strict'):
    try:
        charset = chardet.detect(data)

        if not charset['encoding']:
            raise EncodingError('Header claimed {claimed!r} charset, but detection found none; '
                                'Decoding failed.'.format(claimed=claimed))

        return data.decode(charset['encoding'], errors)

    except UnicodeError as exc:
        raise EncodingError('Header lied and claimed {claimed!r} charset, guessing said '
                            '{charset!r} charset, neither worked so this is a bad email: '
                            '{exc!s}.'.format(claimed=claimed,
                                              charset=charset,
                                              exc=exc))
