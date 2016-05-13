import six
from sqlalchemy import type_coerce

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

    def apply(self, q, cuts):
        """ Apply a set of filters, which can be given as a set of tuples in
        the form (ref, operator, value), or as a string in query form. If it
        is ``None``, no filter will be applied. """
        info = []
        for (ref, operator, value) in self.parse(cuts):
            info.append({'ref': ref, 'operator': operator, 'value': value})
            table, column = self.cube.model[ref].bind(self.cube)
            self.add_binding(table, ref)
            q = q.where(column == type_coerce(value, column.type))
        q = self.restrict_joins(q)
        return info, q
