import six

from babbage.query.parser import Parser
from babbage.exc import QueryException

import datetime


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

    def _check_type(self, ref, value):
        model_type = self.cube.model[ref].datatype
        if type(value) is str and model_type == 'string':
            return
        if type(value) is unicode and model_type == 'string':
            return
        elif type(value) is int and model_type == 'integer':
            return
        elif type(value) is datetime.datetime and model_type == 'date':
            return
        else:
            raise QueryException('Invalid value %r for cut %s of type %s' % (value, ref, model_type))

    def apply(self, q, cuts):
        """ Apply a set of filters, which can be given as a set of tuples in
        the form (ref, operator, value), or as a string in query form. If it
        is ``None``, no filter will be applied. """
        info = []
        for (ref, operator, value) in self.parse(cuts):
            self._check_type(ref, value)
            info.append({'ref': ref, 'operator': operator, 'value': value})
            table, column = self.cube.model[ref].bind(self.cube)
            q = self.ensure_table(q, table)
            q = q.where(column == value)
        return info, q
