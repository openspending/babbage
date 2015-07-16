from nose.tools import raises

from .util import TestCase, load_json_fixture, load_csv

from babbage.cube import Cube
from babbage.exc import BindingException


class CubeTestCase(TestCase):

    def setUp(self):
        super(CubeTestCase, self).setUp()
        self.cra_model = load_json_fixture('models/cra.json')
        self.cra_table = load_csv('cra.csv')
        self.cube = Cube(self.engine, 'cra', self.cra_model)

    def test_table_exists(self):
        assert self.engine.has_table(self.cra_table.name)

    def test_table_load(self):
        table = self.cube._load_table(self.cra_table.name)
        assert table is not None

    def test_table_pk(self):
        assert self.cube._fact_pk is not None

    @raises(BindingException)
    def test_table_load_nonexist(self):
        self.cube._load_table('lalala')

    @raises(BindingException)
    def test_dimension_column_nonexist(self):
        model = self.cra_model.copy()
        model['dimensions']['cofog1']['attributes']['name']['column'] = 'lala'
        self.cube = Cube(self.engine, 'cra', model)
        self.cube.model['cofog1.name'].bind_one(self.cube)

    def test_dimension_column_qualified(self):
        model = self.cra_model.copy()
        name = 'cra.cofog1_name'
        model['dimensions']['cofog1']['attributes']['name']['column'] = name
        self.cube = Cube(self.engine, 'cra', model)
        self.cube.model['cofog1.name'].bind_one(self.cube)

    def test_facts_basic(self):
        facts = self.cube.facts()
        assert facts['total_fact_count'] == 36
        assert len(facts['data']) == 36, len(facts['data'])
        row0 = facts['data'][0]
        assert 'cofog1.name' in row0, row0
        assert 'amount' in row0, row0
        assert 'amount.sum' not in row0, row0
        assert '_count' not in row0, row0

    def test_facts_basic_filter(self):
        facts = self.cube.facts(cuts='cofog1:"4"')
        assert facts['total_fact_count'] == 12
        assert len(facts['data']) == 12, len(facts['data'])

    def test_facts_basic_fields(self):
        facts = self.cube.facts(refs='cofog1,cofog2')
        assert facts['total_fact_count'] == 36, facts['total_fact_count']
        row0 = facts['data'][0]
        assert 'cofog1.name' in row0, row0
        assert 'amount' not in row0, row0
        assert 'amount.sum' not in row0, row0

    def test_facts_paginate(self):
        facts = self.cube.facts(page_size=5)
        assert facts['total_fact_count'] == 36, facts['total_fact_count']
        assert len(facts['data']) == 5, len(facts['data'])

    def test_members_basic(self):
        members = self.cube.members('cofog1')
        assert members['total_member_count'] == 4, members['total_member_count']
        assert len(members['data']) == 4, len(members['data'])
        row0 = members['data'][0]
        assert 'cofog1.name' in row0, row0
        assert 'amount' not in row0, row0

    def test_members_paginate(self):
        members = self.cube.members('cofog1', page_size=2)
        assert members['total_member_count'] == 4, members['total_member_count']
        assert len(members['data']) == 2, len(members['data'])

    def test_aggregate_basic(self):
        aggs = self.cube.aggregate(drilldowns='cofog1')
        assert aggs['total_cell_count'] == 4, aggs['total_member_count']
        assert len(aggs['cells']) == 4, len(aggs['data'])
        row0 = aggs['cells'][0]
        assert 'cofog1.name' in row0, row0
        assert 'amount.sum' in row0, row0
        assert 'amount' not in row0, row0

    def test_aggregate_empty(self):
        aggs = self.cube.aggregate(drilldowns='cofog1', page_size=0)
        assert aggs['total_cell_count'] == 4, aggs['total_member_count']
        assert len(aggs['cells']) == 0, len(aggs['data'])
