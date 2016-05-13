import os
import json

import grako
import six
import dateutil.parser
from grako.exceptions import GrakoException

from babbage.exc import QueryException, BindingException
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
        self.bindings = []

    def add_binding(self, q, binding):
        self.bindings.append(binding)
        return q

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

    def date_value(self, ast):
        return dateutil.parser.parse(ast).date()

    def date_set(self, ast):
        return map(self.date_value, ast)

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

    def restrict_joins(self, q):
        #  if len(q.froms) == 0:
        #      raise BindingException("woops % r", self.bindings)
        if len(q.froms) == 1:
            return q
        else:
            for binding in self.bindings:
                if binding[0] == self.cube.fact_table:
                    continue
                print("table=%r ref=%r" % (binding[0].name, binding[1]))
                concept = self.cube.model[binding[1]]
                print("contept=%r" % concept)
                dimension = concept.dimension  # assume it's an attribute
                print("dimension=%r key_attribute=%r" % (dimension, dimension.key_attribute))
                dimension_table, key_column = dimension.key_attribute.bind(self.cube)
                if binding[0] != dimension_table:
                    raise BindingException('Attributes must be of same table as '
                                           'as their dimension key')
                join_column = self.cube.fact_table.columns[dimension.join_column_name]
                q = q.where(join_column == key_column)
        return q

    @staticmethod
    def allrefs(*args):
        return [ref for concept_list in args for concept in concept_list for ref in concept.refs]
