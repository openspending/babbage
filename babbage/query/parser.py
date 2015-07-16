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
        self.info = {}
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

    def ensure_table(self, q, table):
        if table not in q.froms:
            q = q.select_from(table)
        return q
