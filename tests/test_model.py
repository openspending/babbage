import pytest


class TestModel(object):
    def test_model_concepts(self, simple_model):
        concepts = list(simple_model.concepts)
        assert len(concepts) == 11, len(concepts)

    def test_model_match(self, simple_model):
        concepts = list(simple_model.match('foo'))
        assert len(concepts) == 1, len(concepts)

    def test_model_match_invalid(self, simple_model):
        concepts = list(simple_model.match('fooxx'))
        assert len(concepts) == 0, len(concepts)

    def test_model_aggregates(self, simple_model):
        aggregates = list(simple_model.aggregates)
        assert len(aggregates) == 2, aggregates

    def test_model_fact_table(self, simple_model):
        assert simple_model.fact_table_name == 'simple'
        assert 'simple' in repr(simple_model), repr(simple_model)

    def test_model_hierarchies(self, simple_model):
        hierarchies = list(simple_model.hierarchies)
        assert len(hierarchies) == 1

    def test_model_dimension_hierarchies(self, simple_model):
        bar = simple_model.match('bar')[0]
        baz = simple_model.match('baz')[0]
        assert bar.ref.startswith('bar.')
        assert baz.alias.startswith('bazwaz.')

    def test_deref(self, simple_model):
        assert simple_model['foo'].name == 'foo'
        assert simple_model['foo.key'].name == 'key'
        assert simple_model['amount'].name == 'amount'
        assert 'amount' in simple_model
        assert 'amount.sum' in simple_model
        assert '_count' in simple_model
        assert 'yabba' not in simple_model
        assert 'foo.key' in simple_model

    def test_repr(self, simple_model):
        assert 'amount' in repr(simple_model['amount'])
        assert 'amount.sum' in repr(simple_model['amount.sum'])
        assert 'foo.key' in repr(simple_model['foo.key'])
        assert 'foo' in repr(simple_model['foo'])
        assert 'foo' in str(simple_model['foo'])
        assert simple_model['foo'] == 'foo'

    def test_to_dict(self, simple_model):
        data = simple_model.to_dict()
        assert 'measures' in data
        assert 'amount' in data['measures']
        assert 'amount.sum' in data['aggregates']
        assert 'ref' in data['measures']['amount']
        assert 'dimensions' in data
        assert 'hierarchies' in data
        assert 'foo' in data['dimensions']
