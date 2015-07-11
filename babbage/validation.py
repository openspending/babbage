import os
import json
from jsonschema import Draft4Validator

schema_path = os.path.join(os.path.dirname(__file__), 'schema')


def load_validator(name):
    with open(os.path.join(schema_path, name)) as fh:
        schema = json.load(fh)
    Draft4Validator.check_schema(schema)
    return Draft4Validator(schema)


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
