import os
import six

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema')


def parse_int(text, fallback=None):
    """ Try to extract an integer from a string, return the fallback if that's
    not possible. """
    try:
        if isinstance(text, six.integer_types):
            return text
        elif isinstance(text, six.string_types):
            return int(text)
        else:
            return fallback
    except ValueError:
        return fallback
