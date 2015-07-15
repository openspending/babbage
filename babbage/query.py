from babbage.parser import CutsParser
from babbage.util import parse_int


class Query(object):
    """ A query builder object. """

    def __init__(self, cube):
        self.cube = cube
        self._cuts = []
        self._fields = []
        self._drilldown = []
        self._limit = 10000
        self._offset = 0
        self._order = []

    def cut(self, cuts):
        """ Apply a set of filters, which can be given as a set of tuples in
        the form (ref, operator, value), or as a string in query form. If it
        is ``None``, no filter will be applied. """
        self._cuts.extend(CutsParser().parse(cuts))

    def project(self, fields):
        """ Define a set of fields to return for a non-aggregated query. """
        pass

    def aggregate(self, aggregates):
        """ Define a set of fields to perform aggregation on. """
        pass

    def drilldown(self, drilldowns):
        """ Apply a set of grouping criteria and project them. """
        pass

    def paginate(self, page, page_size):
        """ Apply limit and offset to the query, based on page-based offset
        specifications. """
        self._limit = parse_int(page_size)
        self._offset = (parse_int(page) - 1) * self._limit

    def order(self, orders):
        """ Sort on a set of field specifications of the type (ref, direction)
        in order of the submitted list. """
        pass

    def count(self):
        pass

    def generate(self):
        pass
