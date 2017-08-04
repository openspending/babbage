from datetime import date
import pytest

from babbage.exc import QueryException
from babbage.cube import Cube
from babbage.query import Cuts, Ordering, Aggregates, Drilldowns


class TestParser(object):

    def test_cuts_unquoted_string(self, cube):
        cuts = Cuts(cube).parse('foo:bar')
        assert len(cuts) == 1, cuts
        cuts = [(c[0], c[1], list(c[2])) for c in cuts]
        assert ('foo', ':', ['bar']) in cuts, cuts

    def test_cuts_quoted_string(self, cube):
        cuts = Cuts(cube).parse('foo:"bar lala"')
        assert len(cuts) == 1, cuts
        cuts = [(c[0], c[1], list(c[2])) for c in cuts]
        assert ('foo', ':', ['bar lala']) in cuts, cuts

    def test_cuts_string_set(self, cube):
        cuts = Cuts(cube).parse('foo:"bar";"lala"')
        assert len(cuts) == 1, cuts
        cuts = [(c[0], c[1], list(c[2])) for c in cuts]
        assert ('foo', ':', ['bar', 'lala']) in cuts, cuts

    def test_cuts_int_set(self, cube):
        cuts = Cuts(cube).parse('foo:3;22')
        assert len(cuts) == 1, cuts
        cuts = [(c[0], c[1], list(c[2])) for c in cuts]
        assert ('foo', ':', [3, 22]) in cuts, cuts

    def test_cuts_multiple(self, cube):
        cuts = Cuts(cube).parse('foo:bar|bar:5')
        assert len(cuts) == 2, cuts
        cuts = [(c[0], c[1], list(c[2])) for c in cuts]
        assert ('bar', ':', [5]) in list(cuts), cuts

    def test_cuts_multiple_int_first(self, cube):
        cuts = Cuts(cube).parse('bar:5|foo:bar')
        assert len(cuts) == 2, cuts
        cuts = [(c[0], c[1], list(c[2])) for c in cuts]
        assert ('bar', ':', [5]) in list(cuts), cuts

    def test_cuts_quotes(self, cube):
        cuts = Cuts(cube).parse('foo:"bar|lala"|bar:5')
        assert len(cuts) == 2, cuts

    def test_cuts_date(self, cube):
        cuts = Cuts(cube).parse('foo:2015-01-04')
        assert list(cuts[0][2]) == [date(2015, 1, 4)], cuts

    def test_cuts_date_set(self, cube):
        cuts = Cuts(cube).parse('foo:2015-01-04;2015-01-05')
        assert len(cuts) == 1, cuts
        assert list(cuts[0][2]) == [date(2015, 1, 4), date(2015, 1, 5)], cuts

    def test_cuts_int(self, cube):
        cuts = Cuts(cube).parse('foo:2015')
        assert list(cuts[0][2]) == [2015], cuts

    def test_cuts_int_prefixed_string(self, cube):
        cuts = Cuts(cube).parse('foo:2015M01')
        assert list(cuts[0][2]) == ['2015M01'], cuts

    def test_cuts_invalid(self, cube):
        with pytest.raises(QueryException):
            Cuts(cube).parse('f oo:2015-01-04')

    def test_null_filter(self, cube):
        cuts = Cuts(cube).parse(None)
        assert isinstance(cuts, list)
        assert not len(cuts)

    def test_order(self, cube):
        ordering = Ordering(cube).parse('foo:desc,bar')
        assert ordering[0][1] == "desc", ordering
        assert ordering[1][1] == "asc", ordering

    def test_order_invalid(self, cube):
        with pytest.raises(QueryException):
            Ordering(cube).parse('fooxx:desc')

    def test_drilldowns(self, cube):
        dd = Drilldowns(cube).parse('foo|bar')
        assert len(dd) == 2

    def test_drilldowns_invalid(self, cube):
        with pytest.raises(QueryException):
            Drilldowns(cube).parse('amount')

    def test_aggregates_invalid(self, cube):
        with pytest.raises(QueryException):
            Aggregates(cube).parse('amount')

    def test_aggregates_dimension(self, cube):
        with pytest.raises(QueryException):
            Aggregates(cube).parse('cofog1.name')

    def test_aggregates(self, cube):
        agg = Aggregates(cube).parse('amount.sum')
        assert len(agg) == 1
        agg = Aggregates(cube).parse('amount.sum|_count')
        assert len(agg) == 2


@pytest.fixture
def cube(sqla_engine, simple_model):
    return Cube(sqla_engine, 'simple', simple_model)
