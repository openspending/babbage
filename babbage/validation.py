import os
import json
from jsonschema import Draft4Validator, FormatChecker

from babbage.util import SCHEMA_PATH

checker = FormatChecker()


@checker.checks('attribute_exists')
def check_attribute_exists(instance):
    """ Additional check for the dimension model, to ensure that attributes
    given as the key and label attribute on the dimension exist. """
    attributes = instance.get('attributes', {}).keys()
    if instance.get('key_attribute') not in attributes:
        return False
    label_attr = instance.get('label_attribute')
    if label_attr and label_attr not in attributes:
        return False
    return True


def load_validator(name):
    """ Load the JSON Schema Draft 4 validator with the given name from the
    local schema directory. """
    with open(os.path.join(SCHEMA_PATH, name)) as fh:
        schema = json.load(fh)
    Draft4Validator.check_schema(schema)
    return Draft4Validator(schema, format_checker=checker)


def validate_model(model):
    validator = load_validator('model.json')
    validator.validate(model)
