from babbage.query.parser import Parser
from babbage.exc import QueryException


class Fields(Parser):
    """ Handle parser output for field specifications. """
    start = "fields"

    def field(self, ast):
        refs = [m.ref for m in self.cube.model.measures] + \
               [d.ref for d in self.cube.model.dimensions] + \
               [a.ref for a in self.cube.model.attributes]
        if ast not in refs:
            raise QueryException('Invalid field: %r' % ast)
        self.results.append(ast)

    def apply(self, q, fields):
        """ Define a set of fields to return for a non-aggregated query. """
        for field in self.parse(fields):
            for (table, column) in self.cube.model[field].bind_many(self.cube):
                q = self.ensure_table(q, table)
                q = q.column(column)

        if not len(self.results):
            # If no fields are requested, return all available fields.
            for c in list(self.cube.model.attributes) + \
                    list(self.cube.model.measures):
                table, column = c.bind_one(self.cube)
                q = self.ensure_table(q, table)
                q = q.column(column)
        return q
