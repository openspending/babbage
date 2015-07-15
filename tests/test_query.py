from nose.tools import raises

from .util import TestCase, load_json_fixture, load_csv

from babbage.exc import QueryException
from babbage.cube import Cube
from babbage.query import Query


class QueryTestCase(TestCase):

    def setUp(self):
        super(QueryTestCase, self).setUp()
        model = load_json_fixture('models/cra.json')
        self.cra_table = load_csv('cra.csv')
        self.cube = Cube(self.engine, 'cra', model)

    def test_cuts(self):
        q = Query(self.cube)
        q.cut('cofog1:bar')
        assert len(q._cuts) == 1, q._cuts

    @raises(QueryException)
    def test_invalid_cuts(self):
        q = Query(self.cube)
        q.cut('foxo:bar')
        assert len(q._cuts) == 1, q._cuts

    def test_drilldown_dimension(self):
        q = Query(self.cube)
        q.drilldown('cofog1')
        assert len(q._fields) == 4, q._fields

    def test_drilldown_attribute(self):
        q = Query(self.cube)
        q.drilldown('cofog1.name')
        assert len(q._fields) == 1, q._fields

    def test_fields(self):
        q = Query(self.cube)
        q.project('cofog1.name,cofog2.label')
        assert len(q._fields) == 2, q._fields

    def test_aggregates(self):
        q = Query(self.cube)
        q.aggregate('amount.sum|_count')
        assert len(q._fields) == 2, q._fields

    def test_ordering(self):
        q = Query(self.cube)
        q.order('amount.sum:desc,cofog1.name')
        assert len(q._orders) == 2, q._order

    def test_pagination(self):
        q = Query(self.cube)
        q.paginate('5', '1000')
        assert q._limit == 1000, q._limit
        assert q._offset == 4000, q._offset
        q.paginate('5', '1000000')
        assert q._limit == 10000, q._limit

    @raises(QueryException)
    def test_fields_aggregare(self):
        q = Query(self.cube)
        q.project('cofog1.name,amount.sum')

    # def test_make_query(self):
    #     q = Query(self.cube)
    #     q.project('cofog1.name,cofog2')
    #     q.cut('cofog1.name:01')
    #     q.order('amount:desc,cofog1.name')
    #     print q._get_unpaginated_query()
    #     assert False
