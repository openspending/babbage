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

@checker.checks('valid_hierarchies')
def check_valid_hierarchies(instance):
    """ Additional check for the hierarchies model, to ensure that levels
    given are pointing to actual dimensions """
    hierarchies = instance.get('hierarchies', {}).values()
    dimensions = set(instance.get('dimensions',{}).keys())
    all_levels = set()
    for hierarcy in hierarchies:
        levels = set(hierarcy.get('levels',[]))
        if len(all_levels.intersection(levels))>0:
            # Dimension appears in two different hierarchies
            return False
        all_levels = all_levels.union(levels)
        if not dimensions.issuperset(levels):
            # Level which is not in a dimension
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
