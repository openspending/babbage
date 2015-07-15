import os
import json

import grako
import six
import dateutil.parser
from grako.exceptions import GrakoException

from babbage.exc import QueryException
from babbage.util import SCHEMA_PATH

with open(os.path.join(SCHEMA_PATH, 'parser.ebnf'), 'rb') as fh:
    grammar = fh.read()
    model = grako.genmodel("all", grammar)


class Parser(object):
    """ Type casting for the basic primitives of the parser, e.g. strings,
    ints and dates. """

    def __init__(self, cube):
        self.results = []
        self.cube = cube

    def string_value(self, ast):
        text = ast[0]
        if text.startswith('"') and text.endswith('"'):
            return json.loads(text)
        return text

    def int_value(self, ast):
        return int(ast)

    def date_value(self, ast):
        return dateutil.parser.parse(ast).date()

    def parse(self, text):
        if isinstance(text, six.string_types):
            try:
                model.parse(text, start=self.start, semantics=self)
                return self.results
            except GrakoException, ge:
                raise QueryException(ge.message)
        elif text is None:
            text = []
        return text


class CutsParser(Parser):
    """ Handle parser output for cuts. """
    start = "cuts"

    def cut(self, ast):
        value = ast[2]
        if isinstance(value, six.string_types) and len(value.strip()) == 0:
            value = None
        if ast[0] not in self.cube.model:
            raise QueryException('Invalid cut: %r' % ast[0])
        self.results.append((ast[0], ast[1], value))


class DrilldownsParser(Parser):
    """ Handle parser output for drilldowns. """
    start = "drilldowns"

    def drilldown(self, ast):
        print ast
        # self.results.append((ast[0], ast[1], ast[2]))
        return ast
