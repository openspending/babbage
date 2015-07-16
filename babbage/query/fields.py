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
