from .util import TestCase

from babbage.parser import CutsParser


class ParserTestCase(TestCase):

    def setUp(self):
        super(ParserTestCase, self).setUp()

    def test_cuts(self):
        cuts = CutsParser.parse('foo:bar')
        assert len(cuts) == 1, cuts

    def test_cuts_multiple(self):
        cuts = CutsParser.parse('foo:bar|test:5')
        assert len(cuts) == 2, cuts
        assert ('test', ':', 5) in cuts, cuts

    def test_cuts_quotes(self):
        cuts = CutsParser.parse('foo:"bar|lala"|test:5')
        assert len(cuts) == 2, cuts

    def test_cuts_null(self):
        cuts = CutsParser.parse('foo:')
        assert cuts[0][2] is None, cuts
