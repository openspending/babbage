from nose.tools import raises

from .util import TestCase, load_json_fixture, load_csv

from babbage.cube import Cube
from babbage.exc import BindingException, QueryException


class CubeTestCase(TestCase):

    def setUp(self):
        super(CubeTestCase, self).setUp()
        self.cra_model = load_json_fixture('models/cra.json')
        self.cra_table = load_csv('cra.csv')
        self.cra_table = load_csv('cap_or_cur.csv')
        self.cube = Cube(self.engine, 'cra', self.cra_model)

    def test_table_exists(self):
        assert self.engine.has_table(self.cra_table.name)

    def test_table_load(self):
        table = self.cube._load_table(self.cra_table.name)
        assert table is not None
        assert 'cra' in repr(self.cube)

    def test_table_pk(self):
        assert self.cube.fact_pk is not None

    @raises(BindingException)
    def test_table_load_nonexist(self):
        self.cube._load_table('lalala')

    @raises(BindingException)
    def test_dimension_column_nonexist(self):
        model = self.cra_model.copy()
        model['dimensions']['cofog1']['attributes']['name']['column'] = 'lala'
        self.cube = Cube(self.engine, 'cra', model)
        self.cube.model['cofog1.name'].bind(self.cube)

    @raises(BindingException)
    def test_star_column_nonexist(self):
        model = self.cra_model.copy()
        model['dimensions']['cap_or_cur']['join_column'] = 'lala'
        self.cube = Cube(self.engine, 'cra', model)
        self.cube.facts()

    @raises(BindingException)
    def test_attr_table_different_from_dimension_key(self):
        model = self.cra_model.copy()
        model['dimensions']['cap_or_cur']['attributes']['code']['column'] = 'cap_or_cur'
        self.cube = Cube(self.engine, 'cra', model)
        self.cube.facts()

    def test_dimension_column_qualified(self):
        model = self.cra_model.copy()
        name = 'cra.cofog1_name'
        model['dimensions']['cofog1']['attributes']['name']['column'] = name
        self.cube = Cube(self.engine, 'cra', model)
        self.cube.model['cofog1.name'].bind(self.cube)

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

    def test_facts_star_filter(self):
        facts = self.cube.facts(cuts='cap_or_cur.label:"Current Expenditure"')
        assert facts['total_fact_count'] == 21, facts
        assert len(facts['data']) == 21, len(facts['data'])

    def test_facts_star_filter_and_facts_field(self):
        facts = self.cube.facts(cuts='cap_or_cur.label:"Current Expenditure"',
                                fields='cofog1')
        assert facts['total_fact_count'] == 21, facts
        assert len(facts['data']) == 21, len(facts['data'])

    def test_facts_star_filter_and_field(self):
        facts = self.cube.facts(cuts='cap_or_cur.label:"Current Expenditure"',
                                fields='cap_or_cur.code')
        assert facts['total_fact_count'] == 21, facts
        assert len(facts['data']) == 21, len(facts['data'])

    def test_facts_facts_filter_and_star_field(self):
        facts = self.cube.facts(cuts='cofog1:"4"',
                                fields='cap_or_cur.code')
        assert facts['total_fact_count'] == 12, facts
        assert len(facts['data']) == 12, len(facts['data'])

    @raises(QueryException)
    def test_facts_invalid_filter(self):
        self.cube.facts(cuts='cofogXX:"4"')

    def test_facts_basic_fields(self):
        facts = self.cube.facts(fields='cofog1,cofog2')
        assert facts['total_fact_count'] == 36, facts['total_fact_count']
        row0 = facts['data'][0]
        assert 'cofog1.name' in row0, row0
        assert 'amount' not in row0, row0
        assert 'amount.sum' not in row0, row0

    def test_facts_star_fields(self):
        facts = self.cube.facts(fields='cofog1,cap_or_cur.label')
        assert facts['total_fact_count'] == 36, facts['total_fact_count']
        row0 = facts['data'][0]
        assert 'cofog1.name' in row0, row0
        assert 'cap_or_cur.code' not in row0, row0
        assert 'cap_or_cur.label' in row0, row0

    @raises(QueryException)
    def test_facts_invalid_field(self):
        self.cube.facts(fields='cofog1,schnasel')

    def test_facts_paginate(self):
        facts = self.cube.facts(page_size=5)
        assert facts['total_fact_count'] == 36, facts['total_fact_count']
        assert len(facts['data']) == 5, len(facts['data'])

    def test_facts_sort(self):
        facts = self.cube.facts(order='amount:desc')
        assert facts['total_fact_count'] == 36, facts['total_fact_count']
        facts = facts['data']
        assert len(facts) == 36, len(facts['data'])
        assert max(facts, key=lambda f: f['amount']) == facts[0]
        assert min(facts, key=lambda f: f['amount']) == facts[-1]

    def test_members_basic(self):
        members = self.cube.members('cofog1')
        assert members['total_member_count'] == 4, members['total_member_count']
        assert len(members['data']) == 4, len(members['data'])
        row0 = members['data'][0]
        assert 'cofog1.name' in row0, row0
        assert 'amount' not in row0, row0

    def test_members_star_dimension(self):
        members = self.cube.members('cap_or_cur', order='cap_or_cur.label:asc')
        assert members['total_member_count'] == 2, members['total_member_count']
        assert len(members['data']) == 2, len(members['data'])
        assert 'cap_or_cur.code' in members['data'][0], members['data'][0]
        assert 'CAP' == members['data'][0]['cap_or_cur.code'], members['data'][0]

    def test_members_star_dimension_order(self):
        members = self.cube.members('cap_or_cur', order='cap_or_cur.label:desc')
        assert 'CUR' == members['data'][0]['cap_or_cur.code'], members['data'][0]

    def test_members_paginate(self):
        members = self.cube.members('cofog1', page_size=2)
        assert members['total_member_count'] == 4, members['total_member_count']
        assert members['page'] == 1, members
        assert members['page_size'] == 2, members
        assert len(members['data']) == 2, len(members['data'])
        members2 = self.cube.members('cofog1', page_size=2, page=2)
        assert members2['page'] == 2, members2
        assert members2['page_size'] == 2, members2
        assert members2['data'] != members['data'], members2['data']

    def test_aggregate_basic(self):
        aggs = self.cube.aggregate(drilldowns='cofog1')
        assert aggs['total_cell_count'] == 4, aggs['total_cell_count']
        assert len(aggs['cells']) == 4, len(aggs['data'])
        row0 = aggs['cells'][0]
        assert 'cofog1.name' in row0, row0
        assert 'amount.sum' in row0, row0
        assert 'amount' not in row0, row0

    def test_aggregate_star(self):
        aggs = self.cube.aggregate(drilldowns='cap_or_cur', order='cap_or_cur')
        assert aggs['total_cell_count'] == 2, aggs
        assert len(aggs['cells']) == 2, len(aggs['data'])
        row0 = aggs['cells'][0]
        assert row0['cap_or_cur.code'] == 'CAP', row0
        assert row0['amount.sum'] == -608400000, row0
        assert row0['_count'] == 15, row0

    def test_aggregate_count_only(self):
        aggs = self.cube.aggregate(drilldowns='cofog1', aggregates='_count')
        assert aggs['total_cell_count'] == 4, aggs['total_cell_count']
        assert len(aggs['cells']) == 4, len(aggs['data'])
        assert '_count' in aggs['summary'], aggs['summary']
        row0 = aggs['cells'][0]
        assert 'cofog1.name' in row0, row0
        assert 'amount.sum' not in row0, row0
        assert 'amount' not in row0, row0

    def test_aggregate_star_count_only(self):
        aggs = self.cube.aggregate(drilldowns='cap_or_cur',
                                   order='cap_or_cur',
                                   aggregates='_count')
        assert aggs['total_cell_count'] == 2, aggs
        assert len(aggs['cells']) == 2, len(aggs['data'])
        row0 = aggs['cells'][0]
        assert row0['cap_or_cur.code'] == 'CAP', row0
        assert row0['_count'] == 15, row0

    def test_aggregate_empty(self):
        aggs = self.cube.aggregate(drilldowns='cofog1', page_size=0)
        assert aggs['total_cell_count'] == 4, aggs['total_cell_count']
        assert len(aggs['cells']) == 0, len(aggs['data'])

    def test_compute_cardinalities(self):
        cofog = self.cube.model['cofog1']
        assert cofog.cardinality is None
        assert cofog.cardinality_class is None
        self.cube.compute_cardinalities()
        assert cofog.cardinality == 4, cofog.cardinality
        assert cofog.cardinality_class == 'tiny', \
            (cofog.cardinality, cofog.cardinality_class)
