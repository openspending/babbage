import os
from flask import url_for

from babbage.manager import JSONCubeManager
from babbage.api import configure_api


from .util import TestCase, FIXTURE_PATH


class CubeManagerTestCase(TestCase):

    def setUp(self):
        super(CubeManagerTestCase, self).setUp()
        path = os.path.join(FIXTURE_PATH, 'models')
        self.mgr = JSONCubeManager(self.engine, path)
        configure_api(self.app, self.mgr)

    def test_index(self):
        res = self.client.get(url_for('babbage_api.index'))
        assert res.status_code == 200, res
        assert res.json['api'] == 'babbage'

    def test_jsonp(self):
        res = self.client.get(url_for('babbage_api.index', callback='foo'))
        assert res.status_code == 200, res
        assert res.data.startswith('foo && foo('), res.data

    def test_list_cubes(self):
        res = self.client.get(url_for('babbage_api.cubes'))
        assert len(res.json['data']) == 2, res.json

    def test_get_model(self):
        res = self.client.get(url_for('babbage_api.model', name='cra'))
        assert len(res.json['model']['measures'].keys()) == 2, res.json
        assert res.json['name'] == 'cra', res.json

    def test_get_missing_model(self):
        res = self.client.get(url_for('babbage_api.model', name='crack'))
        assert res.status_code == 404, res
