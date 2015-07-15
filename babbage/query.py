from sqlalchemy import and_
from sqlalchemy.sql.expression import select

from babbage.parser import CutsParser, DrilldownsParser, OrdersParser
from babbage.parser import FieldsParser, AggregatesParser
from babbage.util import parse_int


class Query(object):
    """ A query builder object. """

    def __init__(self, cube):
        self.cube = cube
        self._tables = set([cube._get_fact_table()])
        self._cuts = []
        self._fields = set()
        self._drilldowns = set()
        self._limit = 10000
        self._offset = 0
        self._orders = []
        self.distinct = False

    def cut(self, cuts):
        """ Apply a set of filters, which can be given as a set of tuples in
        the form (ref, operator, value), or as a string in query form. If it
        is ``None``, no filter will be applied. """
        for (ref, operator, value) in CutsParser(self.cube).parse(cuts):
            table, column = self.cube.model[ref].bind_one(self.cube)
            self._tables.add(table)
            self._cuts.append(column == value)

    def project(self, fields):
        """ Define a set of fields to return for a non-aggregated query. """
        for field in FieldsParser(self.cube).parse(fields):
            columns = self.cube.model[field].bind_many(self.cube)
            self._tables.update([t for t, c in columns])
            self._fields.update([c for t, c in columns])

    def aggregate(self, aggregates):
        """ Define a set of fields to perform aggregation on. """
        for aggregate in AggregatesParser(self.cube).parse(aggregates):
            table, column = self.cube.model[aggregate].bind_one(self.cube)
            self._tables.add(table)
            self._fields.add(column)

    def drilldown(self, drilldowns):
        """ Apply a set of grouping criteria and project them. """
        for drilldown in DrilldownsParser(self.cube).parse(drilldowns):
            columns = self.cube.model[drilldown].bind_many(self.cube)
            self._tables.update([t for t, c in columns])
            self._drilldowns.update([c for t, c in columns])
            self._fields.update([c for t, c in columns])

    def paginate(self, page, page_size):
        """ Apply limit and offset to the query, based on page-based offset
        specifications. """
        self._limit = max(0, min(10000, parse_int(page_size)))
        self._offset = (parse_int(page) - 1) * self._limit

    def order(self, orders):
        """ Sort on a set of field specifications of the type (ref, direction)
        in order of the submitted list. """
        for (ref, direction) in OrdersParser(self.cube).parse(orders):
            table, column = self.cube.model[ref].bind_one(self.cube)
            column = column.asc() if direction == 'asc' else column.desc()
            self._tables.add(table)
            self._orders.append(column)

    def _get_order(self):
        """ Get ordering, with some default ordering if none if given. """
        if not len(self._orders):
            return self.cube._get_fact_pk().asc()
        return self._orders

    def _get_unpaginated_query(self):
        # TODO: check if any aggregates are being aggregated.
        # TODO: if no drilldown, and no fields, return all fields.
        return select(columns=set(self._fields),
                      whereclause=and_(*self._cuts),
                      group_by=set(self._drilldowns),
                      order_by=self._get_order(),
                      from_obj=self._tables,
                      distinct=self.distinct)

    def count(self):
        pass

    def generate(self):
        pass
