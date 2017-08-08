from sqlalchemy import func

from babbage.query.parser import Parser
from babbage.model.binding import Binding
from babbage.exc import QueryException


class Fields(Parser):
    """ Handle parser output for field specifications. """
    start = "fields"

    def field(self, ast):
        refs = Parser.allrefs(self.cube.model.measures,
                              self.cube.model.dimensions,
                              self.cube.model.attributes)

        if ast not in refs:
            raise QueryException('Invalid field: %r' % ast)
        self.results.append(ast)

    def apply(self, q, bindings, fields, distinct=False):
        """ Define a set of fields to return for a non-aggregated query. """
        info = []

        group_by = None

        for field in self.parse(fields):
            for concept in self.cube.model.match(field):
                info.append(concept.ref)
                table, column = concept.bind(self.cube)
                bindings.append(Binding(table, concept.ref))
                if distinct:
                    if group_by is None:
                        q = q.group_by(column)
                        group_by = column
                    else:
                        min_column = func.max(column)
                        min_column = min_column.label(column.name)
                        column = min_column
                q = q.column(column)

        if not len(self.results):
            # If no fields are requested, return all available fields.
            for concept in list(self.cube.model.attributes) + \
                    list(self.cube.model.measures):
                info.append(concept.ref)
                table, column = concept.bind(self.cube)
                bindings.append(Binding(table, concept.ref))
                q = q.column(column)

        return info, q, bindings
