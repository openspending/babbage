from .util import TestCase

from babbage.util import parse_int


class UtilTestCase(TestCase):

    def setUp(self):
        super(UtilTestCase, self).setUp()

    def test_parse_int(self):
        assert parse_int(5) == 5
        assert parse_int('5') == 5
        assert parse_int('5.0') is None
        assert parse_int('a') is None
