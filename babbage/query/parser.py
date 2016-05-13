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

    def add_binding(self, table, ref):
        """
        Record an attribute binding in the current parse.
        Must be called by each parser instance for each column
        used in the database query.
        """
        self.bindings.append(Binding(table, ref))

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
            except GrakoException as ge:
                raise QueryException(ge.message)
        elif text is None:
            text = []
        return text

    def restrict_joins(self, q):
        """
        Restrict the joins across all tables referenced in the database
        query to those specified in the model for the relevant dimensions.
        If a single table is used for the query, no unnecessary joins are
        performed. If more than one table are referenced, this ensures
        their returned rows are connected via the fact table.
        """
        if len(q.froms) == 1:
            return q
        else:
            for binding in self.bindings:
                if binding.table == self.cube.fact_table:
                    continue
                concept = self.cube.model[binding.ref]
                dimension = concept.dimension  # assume concept is an attribute
                dimension_table, key_column = dimension.key_attribute.bind(self.cube)
                if binding.table != dimension_table:
                    raise BindingException('Attributes must be of same table as '
                                           'as their dimension key')
                try:
                    join_column = self.cube.fact_table.columns[dimension.join_column_name]
                except KeyError:
                    raise BindingException("Join column '%s' for %r not in fact table."
                                           % (dimension.join_column_name, dimension))
                q = q.where(join_column == key_column)
        return q

    @staticmethod
    def allrefs(*args):
        return [ref for concept_list in args for concept in concept_list for ref in concept.refs]


class Binding(object):
    def __init__(self, table, ref):
        self.table = table
        self.ref = ref
