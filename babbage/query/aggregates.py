from babbage.query.parser import Parser
from babbage.exc import QueryException


class Aggregates(Parser):
    """ Handle parser output for aggregate/drilldown specifications. """
    start = "aggregates"

    def aggregate(self, ast):
        refs = [a.ref for a in self.cube.model.aggregates]
        if ast not in refs:
            raise QueryException('Invalid aggregate: %r' % ast)
        self.results.append(ast)

    def apply(self, q, aggregates):
        for aggregate in self.parse(aggregates):
            table, column = self.cube.model[aggregate].bind_one(self.cube)
            q = self.ensure_table(q, table)
            q = q.column(column)

        if not len(self.results):
            # If no aggregates are specified, aggregate on all.
            for aggregate in self.cube.model.aggregates:
                table, column = aggregate.bind_one(self.cube)
                q = self.ensure_table(q, table)
                q = q.column(column)
        return q
