import six

from babbage.query.parser import Parser
from babbage.exc import QueryException


class Cuts(Parser):
    """ Handle parser output for cuts. """
    start = "cuts"

    def cut(self, ast):
        value = ast[2]
        if isinstance(value, six.string_types) and len(value.strip()) == 0:
            value = None
        # TODO: can you filter measures or aggregates?
        if ast[0] not in self.cube.model:
            raise QueryException('Invalid cut: %r' % ast[0])
        self.results.append((ast[0], ast[1], value))
