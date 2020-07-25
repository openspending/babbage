import os
import io
import csv
import pytest
from flask import url_for

from babbage.manager import JSONCubeManager
from babbage.api import configure_api


@pytest.mark.usefixtures('load_api_fixtures')
class TestCubeManager(object):
    def test_index(self, client):
        res = client.get(url_for('babbage_api.index'))
        assert res.status_code == 200, res
        assert res.json['api'] == 'babbage'

    def test_jsonp(self, client):
        res = client.get(url_for('babbage_api.index', callback='foo'))
        assert res.status_code == 200, res
        assert res.data.startswith(b'foo && foo('), res.data

    def test_list_cubes(self, client):
        res = client.get(url_for('babbage_api.cubes'))
        assert len(res.json['data']) == 3, res.json

    def test_get_model(self, client):
        res = client.get(url_for('babbage_api.model', name='cra'))
        assert len(res.json['model']['measures'].keys()) == 2, res.json
        assert res.json['name'] == 'cra', res.json

    def test_get_missing_model(self, client):
        res = client.get(url_for('babbage_api.model', name='crack'))
        assert res.status_code == 404, res

    def test_aggregate_missing(self, client):
        res = client.get(url_for('babbage_api.aggregate', name='crack'))
        assert res.status_code == 404, res

    @pytest.mark.usefixtures('load_fixtures')
    def test_aggregate_simple(self, client):
        res = client.get(url_for('babbage_api.aggregate', name='cra'))
        assert res.status_code == 200, res
        assert 'summary' in res.json, res.json
        assert 1 == len(res.json['cells']), res.json

    @pytest.mark.usefixtures('load_fixtures')
    def test_aggregate_returns_csv_format(self, client):
        url = url_for(
            'babbage_api.aggregate',
            name='cra',
            drilldown='cofog1.label',
            order='cofog1.label',
            format='csv'
        )
        res = client.get(url)

        assert res.status_code == 200
        data = res.get_data().decode('utf-8')
        rows = [row for row in csv.DictReader(io.StringIO(data))]
        expected_rows = [
            {
                '_count': '12',
                'amount.sum': '45400000',
                'cofog1.label': 'Economic affairs',
                'total.sum': '45400000'
            },
            {
                '_count': '8',
                'amount.sum': '-608900000',
                'cofog1.label': 'Housing and community amenities',
                'total.sum': '-608900000'
            },
            {
                '_count': '5',
                'amount.sum': '500000',
                'cofog1.label': 'Public order and safety',
                'total.sum': '500000'
            },
            {
                '_count': '11',
                'amount.sum': '191500000',
                'cofog1.label': 'Social protection',
                'total.sum': '191500000'
            }
        ]

        assert rows == expected_rows

    @pytest.mark.usefixtures('load_fixtures')
    def test_aggregate_drilldown(self, client):
        res = client.get(url_for('babbage_api.aggregate', name='cra',
                                      drilldown='cofog1'))
        assert res.status_code == 200, res
        assert 'summary' in res.json, res.json
        assert 4 == len(res.json['cells']), res.json

    @pytest.mark.usefixtures('load_fixtures')
    def test_aggregate_invalid_drilldown(self, client):
        res = client.get(url_for('babbage_api.aggregate', name='cra',
                                      drilldown='cofoxxxg1'))
        assert res.status_code == 400, res

    def test_facts_missing(self, client):
        res = client.get(url_for('babbage_api.facts', name='crack'))
        assert res.status_code == 404, res

    @pytest.mark.usefixtures('load_fixtures')
    def test_facts_simple(self, client):
        res = client.get(url_for('babbage_api.facts', name='cra'))
        assert res.status_code == 200, (res, res.get_data())
        assert 'total_fact_count' in res.json, res.json
        assert 36 == len(res.json['data']), res.json

    @pytest.mark.usefixtures('load_fixtures')
    def test_facts_cut(self, client):
        res = client.get(url_for('babbage_api.facts', name='cra',
                                      cut='cofog1:"10"'))
        assert res.status_code == 200, (res, res.get_data())
        assert 11 == len(res.json['data']), len(res.json['data'])

    def test_members_missing(self, client):
        res = client.get(url_for('babbage_api.members', name='cra',
                                      ref='codfss'))
        assert res.status_code == 400, res

    @pytest.mark.usefixtures('load_fixtures')
    def test_members_simple(self, client):
        res = client.get(url_for('babbage_api.members', name='cra',
                                      ref='cofog1'))
        assert res.status_code == 200, res
        assert 'total_member_count' in res.json, res.json
        assert 4 == len(res.json['data']), res.json
