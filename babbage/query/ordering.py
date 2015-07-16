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
