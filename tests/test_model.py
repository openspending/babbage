from nose.tools import raises
from jsonschema import ValidationError

from .util import TestCase, load_json_fixture
from babbage.model import Model


class ModelTestCase(TestCase):

    def setUp(self):
        super(ModelTestCase, self).setUp()
        self.simple_model_data = load_json_fixture('models/simple_model.json')
        self.simple_model = Model(self.simple_model_data)

    @raises(ValidationError)
    def test_model_invalid(self):
        data = self.simple_model_data.copy()
        del data['measures']
        Model(data)

    def test_model_concepts(self):
        concepts = list(self.simple_model.concepts)
        assert len(concepts) == 5, len(concepts)

    def test_model_fact_table(self):
        assert self.simple_model.fact_table_name == 'simple'

    def test_deref(self):
        assert self.simple_model['foo'].name == 'foo'
        assert self.simple_model['foo.key'].name == 'key'
        assert self.simple_model['amount'].name == 'amount'
        assert 'amount' in self.simple_model
        assert 'yabba' not in self.simple_model
        assert 'foo.key' in self.simple_model

    def test_repr(self):
        assert 'amount' in repr(self.simple_model['amount'])
        assert 'foo.key' in repr(self.simple_model['foo.key'])
        assert 'foo' in repr(self.simple_model['foo'])

    def test_to_dict(self):
        data = self.simple_model.to_dict()
        assert 'measures' in data
        assert 'amount' in data['measures']
        assert 'ref' in data['measures']['amount']
        assert 'dimensions' in data
        assert 'foo' in data['dimensions']
