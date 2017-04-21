import six

from babbage.query.parser import Parser
from babbage.model.binding import Binding
from babbage.exc import QueryException

from sqlalchemy.sql.expression import asc, desc


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

    def apply(self, q, bindings, ordering, distinct=None):
        """ Sort on a set of field specifications of the type (ref, direction)
        in order of the submitted list. """
        info = []
        for (ref, direction) in self.parse(ordering):
            info.append((ref, direction))
            table, column = self.cube.model[ref].bind(self.cube)
            if distinct is not None and distinct != ref:
                column = asc(ref) if direction == 'asc' else desc(ref)
            else:
                column = column.label(column.name)
                column = column.asc() if direction == 'asc' else column.desc()
                bindings.append(Binding(table, ref))
            if self.cube.is_postgresql:
                column = column.nullslast()
            q = q.order_by(column)

        if not len(self.results):
            for column in q.columns:
                column = column.asc()
                if self.cube.is_postgresql:
                    column = column.nullslast()
                q = q.order_by(column)
        return info, q, bindings
