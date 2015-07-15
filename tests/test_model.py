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
        assert len(concepts) == 7, len(concepts)

    def test_model_aggregates(self):
        aggregates = list(self.simple_model.aggregates)
        assert len(aggregates) == 2, aggregates

    def test_model_fact_table(self):
        assert self.simple_model.fact_table_name == 'simple'
        assert 'simple' in repr(self.simple_model), repr(self.simple_model)

    def test_deref(self):
        assert self.simple_model['foo'].name == 'foo'
        assert self.simple_model['foo.key'].name == 'key'
        assert self.simple_model['amount'].name == 'amount'
        assert 'amount' in self.simple_model
        assert 'amount.sum' in self.simple_model
        assert '_count' in self.simple_model
        assert 'yabba' not in self.simple_model
        assert 'foo.key' in self.simple_model

    def test_repr(self):
        assert 'amount' in repr(self.simple_model['amount'])
        assert 'amount.sum' in repr(self.simple_model['amount.sum'])
        assert 'foo.key' in repr(self.simple_model['foo.key'])
        assert 'foo' in repr(self.simple_model['foo'])
        assert 'foo' in unicode(self.simple_model['foo'])
        assert self.simple_model['foo'] == 'foo'

    def test_to_dict(self):
        data = self.simple_model.to_dict()
        assert 'measures' in data
        assert 'amount' in data['measures']
        assert 'amount.sum' in data['aggregates']
        assert 'ref' in data['measures']['amount']
        assert 'dimensions' in data
        assert 'foo' in data['dimensions']
