from babbage.query.parser import Parser
from babbage.exc import QueryException


class Drilldowns(Parser):
    """ Handle parser output for drilldowns. """
    start = "drilldowns"

    def dimension(self, ast):
        refs = Parser.allrefs(self.cube.model.dimensions,
                              self.cube.model.attributes)
        if ast not in refs:
            raise QueryException('Invalid drilldown: %r' % ast)
        if ast not in self.results:
            self.results.append(ast)

    def apply(self, q, drilldowns):
        """ Apply a set of grouping criteria and project them. """
        info = []
        for drilldown in self.parse(drilldowns):
            for attribute in self.cube.model.match(drilldown):
                info.append(attribute.ref)
                table, column = attribute.bind(self.cube)
                q = q.column(column)
                q = q.group_by(column)
                q = self.add_binding(q, (table, attribute.ref))
        q = self.restrict_joins(q)
        return info, q
