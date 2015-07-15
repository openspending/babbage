import os
import six

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema')


def parse_int(text):
    """ Try to extract an integer from a string, return None if that's
    not possible. """
    try:
        if isinstance(text, six.string_types):
            return int(text)
        return text
    except ValueError:
        return
