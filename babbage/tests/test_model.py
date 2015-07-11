from nose.tools import raises

from babbage.tests.util import TestCase, load_json_fixture
from babbage.model import Model


class ModelTestCase(TestCase):

    def setUp(self):
        super(ModelTestCase, self).setUp()
        self.simple_model_data = load_json_fixture('simple_model.json')
        self.simple_model = Model(self.simple_model_data)

    def test_model_concepts(self):
        concepts = list(self.simple_model.concepts)
        assert len(concepts) == 5, len(concepts)

    def test_deref(self):
        assert self.simple_model['foo'].name == 'foo'
        assert self.simple_model['foo.key'].name == 'key'
        assert self.simple_model['amount'].name == 'amount'

    def test_to_dict(self):
        data = self.simple_model.to_dict()
        assert 'measures' in data
        assert 'amount' in data['measures']
        assert 'ref' in data['measures']['amount']
        assert 'dimensions' in data
        assert 'foo' in data['dimensions']
