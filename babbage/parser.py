import os
import json
import grako
import six
import dateutil.parser

from babbage.util import SCHEMA_PATH

with open(os.path.join(SCHEMA_PATH, 'parser.ebnf'), 'rb') as fh:
    grammar = fh.read()
    model = grako.genmodel("all", grammar)


class TypeSemantics(object):
    """ Type casting for the basic primitives of the parser, e.g. strings,
    ints and dates. """

    def __init__(self):
        self.results = []

    def string_value(self, ast):
        text = ast[0]
        if text.startswith('"') and text.endswith('"'):
            return json.loads(text)
        return text

    def int_value(self, ast):
        return int(ast)

    def date_value(self, ast):
        return dateutil.parser.parse(ast).date()

    @classmethod
    def parse(cls, text):
        if isinstance(text, six.string_types):
            semantics = cls()
            model.parse(text, start=cls.start, semantics=semantics)
            return semantics.results
        elif text is None:
            text = []
        return text


class CutsParser(TypeSemantics):
    """ Handle parser output for cuts. """
    start = "cuts"

    def cut(self, ast):
        value = ast[2]
        if isinstance(value, six.string_types) and len(value.strip()) == 0:
            value = None
        self.results.append((ast[0], ast[1], value))
        return ast

#
# class DrilldownsParser(TypeSemantics):
#     """ Handle parser output for cuts. """
#     start = "cuts"
#
#     def drilldown(self, ast):
#         print ast
#         # self.results.append((ast[0], ast[1], ast[2]))
#         return ast
