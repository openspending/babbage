import os
import json
from jsonschema import Draft4Validator, FormatChecker

schema_path = os.path.join(os.path.dirname(__file__), 'schema')
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
    with open(os.path.join(schema_path, name)) as fh:
        schema = json.load(fh)
    Draft4Validator.check_schema(schema)
    return Draft4Validator(schema, format_checker=checker)


def validate_model(model):
    validator = load_validator('model.json')
    validator.validate(model)





#
# class LocalSchema(RefResolver):
#
#     def resolve_remote(self, url):
#         local_path = os.path.join(schema_path, url)
#         if os.path.isfile(local_path):
#             with open(local_path) as fh:
#                 return json.load(fh)
#         return super(LocalSchema, self).resolve_remote(url)
#
#
#
# print schema
# resolver = LocalSchema('', schema, {})
# validator = Draft4Validator(schema, resolver=resolver)
# print validator
#
# test = {
#     'name': 'foo',
#     'dimensions': {
#         'foo': {'label': 'Foo'},
#         'bar': {'label': 'Bar'}
#     },
#     'measures': {
#         'amount': {
#             'label': 'Amount in USD'
#         }
#     }
# }
#
# print validator.validate(test, schema)
