from babbage.query.parser import Parser
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

    def apply(self, q, fields):
        """ Define a set of fields to return for a non-aggregated query. """
        info = []
        for field in self.parse(fields):
            for concept in sorted(self.cube.model.match(field), key=lambda c: c.name):
                info.append(concept.ref)
                table, column = concept.bind(self.cube)
                q = self.ensure_table(q, table)
                q = q.column(column)

        if not len(self.results):
            # If no fields are requested, return all available fields.
            for concept in list(self.cube.model.attributes) + \
                    list(self.cube.model.measures):
                info.append(concept.ref)
                table, column = concept.bind(self.cube)
                q = self.ensure_table(q, table)
                q = q.column(column)
        return info, q
