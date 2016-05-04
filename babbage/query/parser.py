import os
import json

import grako
import six
import dateutil.parser
from grako.exceptions import GrakoException

from babbage.exc import QueryException
from babbage.util import SCHEMA_PATH


with open(os.path.join(SCHEMA_PATH, 'parser.ebnf'), 'rb') as fh:
    grammar = fh.read().decode('utf8')
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

    def string_set(self, ast):
        return map(self.string_value, ast)

    def int_value(self, ast):
        return int(ast)

    def int_set(self, ast):
        return map(self.int_value, ast)

    def date_set(self, ast):
        return map(self.date_value, ast)

    def date_value(self, ast):
        return dateutil.parser.parse(ast).date()

    def parse(self, text):
        if isinstance(text, six.string_types):
            try:
                model.parse(text, start=self.start, semantics=self)
                return self.results
            except GrakoException as ge:
                raise QueryException(ge.message)
        elif text is None:
            text = []
        return text

    def ensure_table(self, q, table):
        if table not in q.froms:
            q = q.select_from(table)
        return q

    @staticmethod
    def allrefs(*args):
        return [ref for concept_list in args for concept in concept_list for ref in concept.refs]
