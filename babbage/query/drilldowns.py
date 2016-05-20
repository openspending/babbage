from babbage.query.parser import Parser
from babbage.model.binding import Binding
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

    def apply(self, q, bindings, drilldowns):
        """ Apply a set of grouping criteria and project them. """
        info = []
        for drilldown in self.parse(drilldowns):
            for attribute in self.cube.model.match(drilldown):
                info.append(attribute.ref)
                table, column = attribute.bind(self.cube)
                bindings.append(Binding(table, attribute.ref))
                q = q.column(column)
                q = q.group_by(column)
        return info, q, bindings
