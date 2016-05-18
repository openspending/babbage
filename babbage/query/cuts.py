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
        """
        Checks whether the type of the cut value matches the type of the
        concept being cut, and raises a QueryException if it doesn't match
        """
        if isinstance(value, list):
            return map(lambda val: self._check_type(ref, val), value)

        model_type = self.cube.model[ref].datatype
        query_type = self._api_type(value)
        if query_type == model_type:
            return
        else:
            raise QueryException("Invalid value %r parsed as type '%s' "
                                 "for cut %s of type '%s'"
                                 % (value, query_type, ref, model_type))

    def _api_type(self, value):
        """
        Returns the API type of the given value based on its python type.

        """
        if isinstance(value, six.string_types):
            return 'string'
        elif isinstance(value, six.integer_types):
            return 'integer'
        elif type(value) is datetime.datetime:
            return 'date'

    def apply(self, q, cuts):
        """ Apply a set of filters, which can be given as a set of tuples in
        the form (ref, operator, value), or as a string in query form. If it
        is ``None``, no filter will be applied. """
        info = []
        for (ref, operator, value) in self.parse(cuts):
            self._check_type(ref, value)
            info.append({'ref': ref, 'operator': operator, 'value': value})
            table, column = self.cube.model[ref].bind(self.cube)
            self.add_binding(table, ref)
            q = q.where(column.in_(value))
        q = self.restrict_joins(q)
        return info, q
