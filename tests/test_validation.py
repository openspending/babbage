import pytest
from jsonschema import ValidationError

from babbage.validation import validate_model


class TestValidation(object):

    def test_simple_model(self, simple_model_data):
        validate_model(simple_model_data)

    def test_invalid_fact_table(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            model['fact_table'] = 'b....'
            validate_model(model)

    def test_no_fact_table(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            del model['fact_table']
            validate_model(model)

    def test_invalid_dimension_name(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            model['dimensions']['goo fdj.'] = {'label': 'bar'}
            validate_model(model)

    def test_invalid_measure_name(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            model['measures']['goo fdj.'] = {'label': 'bar'}
            validate_model(model)

    def test_no_measure(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            model['measures'] = {}
            validate_model(model)

    def test_no_measure_label(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            model['measures']['amount'] = {}
            validate_model(model)

    def test_invalid_aggregate(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            model['measures']['amount']['aggregates'] = 'schnasel'
            validate_model(model)

    def test_invalid_aggregate_string(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            model['measures']['amount']['aggregates'] = 'count'
            validate_model(model)

    def test_invalid_aggregate_string(self, simple_model_data):
        model = simple_model_data
        model['measures']['amount']['aggregates'] = ['count']
        validate_model(model)

    def test_dimension_without_attributes(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            model['dimensions']['foo']['attributes'] = {}
            validate_model(model)

    def test_dimension_without_key(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            del model['dimensions']['foo']['key_attribute']
            validate_model(model)

    def test_dimension_invalid_key(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            model['dimensions']['foo']['key_attribute'] = 'lala'
            validate_model(model)

    def test_dimension_invalid_label(self, simple_model_data):
        with pytest.raises(ValidationError):
            model = simple_model_data
            model['dimensions']['foo']['label_attribute'] = 'lala'
            validate_model(model)
