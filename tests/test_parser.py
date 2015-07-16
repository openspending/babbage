from datetime import date
from nose.tools import raises

from .util import TestCase, load_json_fixture

from babbage.exc import QueryException
from babbage.cube import Cube
from babbage.query import Cuts, Ordering, Aggregates, Drilldowns


class ParserTestCase(TestCase):

    def setUp(self):
        super(ParserTestCase, self).setUp()
        model = load_json_fixture('models/simple_model.json')
        self.cube = Cube(self.engine, 'simple', model)

    def test_cuts(self):
        cuts = Cuts(self.cube).parse('foo:bar')
        assert len(cuts) == 1, cuts

    def test_cuts_quoted(self):
        cuts = Cuts(self.cube).parse('foo:"bar lala"')
        assert len(cuts) == 1, cuts

    def test_cuts_multiple(self):
        cuts = Cuts(self.cube).parse('foo:bar|bar:5')
        assert len(cuts) == 2, cuts
        assert ('bar', ':', 5) in cuts, cuts

    def test_cuts_quotes(self):
        cuts = Cuts(self.cube).parse('foo:"bar|lala"|bar:5')
        assert len(cuts) == 2, cuts

    def test_cuts_date(self):
        cuts = Cuts(self.cube).parse('foo:2015-01-04')
        assert cuts[0][2] == date(2015, 01, 04), cuts

    @raises(QueryException)
    def test_cuts_invalid(self):
        Cuts(self.cube).parse('f oo:2015-01-04')

    def test_cuts_null(self):
        cuts = Cuts(self.cube).parse('foo:')
        assert cuts[0][2] is None, cuts

    def test_null_filter(self):
        cuts = Cuts(self.cube).parse(None)
        assert isinstance(cuts, list)
        assert not len(cuts)

    def test_order(self):
        cuts = Ordering(self.cube).parse('foo:desc,bar')
        assert cuts[0][1] == "desc", cuts
        assert cuts[1][1] == "asc", cuts

    @raises(QueryException)
    def test_order_invalid(self):
        Ordering(self.cube).parse('fooxx:desc')

    def test_drilldowns(self):
        dd = Drilldowns(self.cube).parse('foo|bar')
        assert len(dd) == 2

    @raises(QueryException)
    def test_drilldowns_invalid(self):
        Drilldowns(self.cube).parse('amount')

    @raises(QueryException)
    def test_aggregates_invalid(self):
        Aggregates(self.cube).parse('amount')

    @raises(QueryException)
    def test_aggregates_dimension(self):
        Aggregates(self.cube).parse('cofog1.name')

    def test_aggregates(self):
        agg = Aggregates(self.cube).parse('amount.sum')
        assert len(agg) == 1
        agg = Aggregates(self.cube).parse('amount.sum|_count')
        assert len(agg) == 2
