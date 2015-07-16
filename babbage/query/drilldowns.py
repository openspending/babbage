from babbage.query.parser import Parser
from babbage.exc import QueryException


class Drilldowns(Parser):
    """ Handle parser output for drilldowns. """
    start = "drilldowns"

    def dimension(self, ast):
        refs = [d.ref for d in self.cube.model.dimensions] + \
               [a.ref for a in self.cube.model.attributes]
        if ast not in refs:
            raise QueryException('Invalid drilldown: %r' % ast)
        self.results.append(ast)

    def apply(self, q, drilldowns):
        """ Apply a set of grouping criteria and project them. """
        for drilldown in self.parse(drilldowns):
            drilldown = self.cube.model[drilldown]
            for (table, column) in drilldown.bind_many(self.cube):
                q = self.ensure_table(q, table)
                q = q.column(column)
                q = q.group_by(column)
        return q
