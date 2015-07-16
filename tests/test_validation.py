from jsonschema import ValidationError
from nose.tools import raises

from .util import TestCase, load_json_fixture

from babbage.validation import validate_model


class ValidationTestCase(TestCase):

    def setUp(self):
        super(ValidationTestCase, self).setUp()
        self.simple_model = load_json_fixture('models/simple_model.json')

    def test_simple_model(self):
        validate_model(self.simple_model)

    @raises(ValidationError)
    def test_invalid_fact_table(self):
        model = self.simple_model.copy()
        model['fact_table'] = 'b....'
        validate_model(model)

    @raises(ValidationError)
    def test_no_fact_table(self):
        model = self.simple_model.copy()
        del model['fact_table']
        validate_model(model)

    @raises(ValidationError)
    def test_invalid_dimension_name(self):
        model = self.simple_model.copy()
        model['dimensions']['goo fdj.'] = {'label': 'bar'}
        validate_model(model)

    @raises(ValidationError)
    def test_invalid_measure_name(self):
        model = self.simple_model.copy()
        model['measures']['goo fdj.'] = {'label': 'bar'}
        validate_model(model)

    @raises(ValidationError)
    def test_no_measure(self):
        model = self.simple_model.copy()
        model['measures'] = {}
        validate_model(model)

    @raises(ValidationError)
    def test_no_measure_label(self):
        model = self.simple_model.copy()
        model['measures']['amount'] = {}
        validate_model(model)

    @raises(ValidationError)
    def test_invalid_aggregate(self):
        model = self.simple_model.copy()
        model['measures']['amount']['aggregates'] = 'schnasel'
        validate_model(model)

    @raises(ValidationError)
    def test_invalid_aggregate_string(self):
        model = self.simple_model.copy()
        model['measures']['amount']['aggregates'] = 'count'
        validate_model(model)

    def test_invalid_aggregate_string(self):
        model = self.simple_model.copy()
        model['measures']['amount']['aggregates'] = ['count']
        validate_model(model)

    @raises(ValidationError)
    def test_dimension_without_attributes(self):
        model = self.simple_model.copy()
        model['dimensions']['foo']['attributes'] = {}
        validate_model(model)

    @raises(ValidationError)
    def test_dimension_without_key(self):
        model = self.simple_model.copy()
        del model['dimensions']['foo']['key_attribute']
        validate_model(model)

    @raises(ValidationError)
    def test_dimension_invalid_key(self):
        model = self.simple_model.copy()
        model['dimensions']['foo']['key_attribute'] = 'lala'
        validate_model(model)

    @raises(ValidationError)
    def test_dimension_invalid_label(self):
        model = self.simple_model.copy()
        model['dimensions']['foo']['label_attribute'] = 'lala'
        validate_model(model)
