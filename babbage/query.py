from babbage.parser import CutsParser, DrilldownsParser, OrdersParser
from babbage.parser import FieldsParser, AggregatesParser
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
        self._cuts.extend(CutsParser(self.cube).parse(cuts))

    def project(self, fields):
        """ Define a set of fields to return for a non-aggregated query. """
        self._fields.extend(FieldsParser(self.cube).parse(fields))

    def aggregate(self, aggregates):
        """ Define a set of fields to perform aggregation on. """
        self._fields.extend(AggregatesParser(self.cube).parse(aggregates))

    def drilldown(self, drilldowns):
        """ Apply a set of grouping criteria and project them. """
        drilldowns = DrilldownsParser(self.cube).parse(drilldowns)
        self._drilldown.extend(drilldowns)
        self._fields.extend(drilldowns)

    def paginate(self, page, page_size):
        """ Apply limit and offset to the query, based on page-based offset
        specifications. """
        self._limit = max(0, min(10000, parse_int(page_size)))
        self._offset = (parse_int(page) - 1) * self._limit

    def order(self, orders):
        """ Sort on a set of field specifications of the type (ref, direction)
        in order of the submitted list. """
        self._order.extend(OrdersParser(self.cube).parse(orders))

    def count(self):
        pass

    def generate(self):
        pass
