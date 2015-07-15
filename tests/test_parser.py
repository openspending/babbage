from datetime import date
from nose.tools import raises

from .util import TestCase, load_json_fixture

from babbage.exc import QueryException
from babbage.cube import Cube
from babbage.parser import CutsParser


class ParserTestCase(TestCase):

    def setUp(self):
        super(ParserTestCase, self).setUp()
        model = load_json_fixture('models/simple_model.json')
        self.cube = Cube(self.engine, 'simple', model)

    def test_cuts(self):
        cuts = CutsParser(self.cube).parse('foo:bar')
        assert len(cuts) == 1, cuts

    def test_cuts_multiple(self):
        cuts = CutsParser(self.cube).parse('foo:bar|bar:5')
        assert len(cuts) == 2, cuts
        assert ('bar', ':', 5) in cuts, cuts

    def test_cuts_quotes(self):
        cuts = CutsParser(self.cube).parse('foo:"bar|lala"|bar:5')
        assert len(cuts) == 2, cuts

    def test_cuts_date(self):
        cuts = CutsParser(self.cube).parse('foo:2015-01-04')
        assert cuts[0][2] == date(2015, 01, 04), cuts

    @raises(QueryException)
    def test_cuts_invalid(self):
        CutsParser(self.cube).parse('f oo:2015-01-04')

    def test_cuts_null(self):
        cuts = CutsParser(self.cube).parse('foo:')
        assert cuts[0][2] is None, cuts

    def test_null_filter(self):
        cuts = CutsParser(self.cube).parse(None)
        assert isinstance(cuts, list)
        assert not len(cuts)
