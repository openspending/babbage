from nose.tools import raises

from .util import TestCase, load_json_fixture

from babbage.exc import QueryException
from babbage.cube import Cube
from babbage.query import Query


class QueryTestCase(TestCase):

    def setUp(self):
        super(QueryTestCase, self).setUp()
        model = load_json_fixture('models/simple_model.json')
        self.cube = Cube(self.engine, 'simple', model)

    def test_cuts(self):
        q = Query(self.cube)
        q.cut('foo:bar')
        assert len(q._cuts) == 1, q._cuts

    @raises(QueryException)
    def test_invalid_cuts(self):
        q = Query(self.cube)
        q.cut('foxo:bar')
        assert len(q._cuts) == 1, q._cuts

    def test_drilldown_dimension(self):
        q = Query(self.cube)
        q.drilldown('foo')
        assert len(q._fields) == 1, q._fields

    def test_drilldown_attribute(self):
        q = Query(self.cube)
        q.drilldown('foo.key')
        assert len(q._fields) == 1, q._fields

    def test_fields(self):
        q = Query(self.cube)
        q.project('foo.key,bar.key')
        assert len(q._fields) == 2, q._fields

    def test_aggregates(self):
        q = Query(self.cube)
        q.aggregate('amount.sum|_count')
        assert len(q._fields) == 2, q._fields

    def test_ordering(self):
        q = Query(self.cube)
        q.order('amount.sum:desc,foo.key')
        assert len(q._order) == 2, q._order
        assert q._order[0][1] == 'desc'
        assert q._order[1][1] == 'asc'

    def test_pagination(self):
        q = Query(self.cube)
        q.paginate('5', '1000')
        assert q._limit == 1000, q._limit
        assert q._offset == 4000, q._offset
        q.paginate('5', '1000000')
        assert q._limit == 10000, q._limit

    @raises(QueryException)
    def test_fields_dimension(self):
        q = Query(self.cube)
        q.project('foo.key,bar')
