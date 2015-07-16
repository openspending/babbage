import six

from babbage.query.parser import Parser
from babbage.exc import QueryException


class Ordering(Parser):
    """ Handle parser output for sorting specifications, a tuple of a ref
    and a direction (which is 'asc' if unspecified). """
    start = "ordering"

    def order(self, ast):
        if isinstance(ast, six.string_types):
            ref, direction = ast, 'asc'
        else:
            ref, direction = ast[0], ast[2]
        if ref not in self.cube.model:
            raise QueryException('Invalid sorting criterion: %r' % ast)
        self.results.append((ref, direction))

    def apply(self, q, ordering):
        """ Sort on a set of field specifications of the type (ref, direction)
        in order of the submitted list. """
        for (ref, direction) in self.parse(ordering):
            table, column = self.cube.model[ref].bind_one(self.cube)
            column = column.asc() if direction == 'asc' else column.desc()
            q = self.ensure_table(q, table)
            q = q.order_by(column.nullslast())

        if not len(self.results):
            for column in q.columns:
                q = q.order_by(column.asc().nullslast())
        return q
