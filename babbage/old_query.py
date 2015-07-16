from sqlalchemy import and_, func
from sqlalchemy.sql.expression import select

from babbage.parser import Cuts, Drilldowns, Ordering, Fields, Aggregates
from babbage.util import parse_int


class Query(object):
    """ A query builder object. """

    def __init__(self, cube, distinct=False):
        self.cube = cube
        self._tables = set()
        self._cuts = []
        self._fields = set()
        self._drilldowns = set()
        self._limit = 10000
        self._offset = 0
        self._orders = []
        self.distinct = distinct

    def cut(self, cuts):
        """ Apply a set of filters, which can be given as a set of tuples in
        the form (ref, operator, value), or as a string in query form. If it
        is ``None``, no filter will be applied. """
        for (ref, operator, value) in Cuts(self.cube).parse(cuts):
            table, column = self.cube.model[ref].bind_one(self.cube)
            self._tables.add(table)
            self._cuts.append(column == value)

    def project(self, fields):
        """ Define a set of fields to return for a non-aggregated query. """
        for field in Fields(self.cube).parse(fields):
            self.order(field)
            columns = self.cube.model[field].bind_many(self.cube)
            self._tables.update([t for t, c in columns])
            self._fields.update([c for t, c in columns])

        # TODO: should this be optional?
        if not len(self._fields):
            # If no fields are requested, return all available fields.
            for attribute in self.cube.model.attributes:
                table, column = attribute.bind_one(self.cube)
                self._tables.add(table)
                self._fields.add(column)
            for measure in self.cube.model.measures:
                table, column = measure.bind_one(self.cube)
                self._tables.add(table)
                self._fields.add(column)

    def aggregate(self, aggregates):
        """ Define a set of fields to perform aggregation on. """
        aggregates = Aggregates(self.cube).parse(aggregates)
        for aggregate in aggregates:
            table, column = self.cube.model[aggregate].bind_one(self.cube)
            self._tables.add(table)
            self._fields.add(column)

        if not len(aggregates):
            # If no aggregates are specified, aggregate on all.
            for aggregate in self.cube.model.aggregates:
                table, column = aggregate.bind_one(self.cube)
                self._tables.add(table)
                self._fields.add(column)

    def drilldown(self, drilldowns):
        """ Apply a set of grouping criteria and project them. """
        for drilldown in Drilldowns(self.cube).parse(drilldowns):
            self.order(drilldown)
            drilldown = self.cube.model[drilldown]
            columns = drilldown.bind_many(self.cube)
            self._tables.update([t for t, c in columns])
            self._drilldowns.update([c for t, c in columns])
            self._fields.update([c for t, c in columns])

    def paginate(self, page, page_size, page_max=10000):
        """ Apply limit and offset to the query, based on page-based offset
        specifications. """
        page_size = parse_int(page_size)
        if page_size is None:
            page_size = page_max
        self._limit = max(0, min(page_max, page_size))
        self._offset = (max(1, parse_int(page)) - 1) * self._limit

    def order(self, ordering):
        """ Sort on a set of field specifications of the type (ref, direction)
        in order of the submitted list. """
        for (ref, direction) in Ordering(self.cube).parse(ordering):
            table, column = self.cube.model[ref].bind_one(self.cube)
            column = column.asc() if direction == 'asc' else column.desc()
            column = column.nullslast()
            # if column in self._orders:
            #     self._orders.remove(column)
            self._tables.add(table)
            self._orders.insert(0, column)

    def _get_unpaginated_query(self):
        # A stable sorting of the fields makes counts stable.
        return select(columns=self._fields,
                      whereclause=and_(*self._cuts),
                      group_by=self._drilldowns,
                      order_by=self._orders,
                      from_obj=self._tables,
                      distinct=self.distinct)

    def count(self):
        """ Get the count of records matching the current query, not taking
        account of any pagination parameters given. """
        q = self._get_unpaginated_query().alias()
        q = select(columns=[func.count(True)], from_obj=q)
        return self.cube.engine.execute(q).scalar()

    def summary(self):
        """ Generate the totals for all aggregates with no pagination applied.
        This must be called before drilldowns are applied. """
        q = self._get_unpaginated_query()
        rp = self.cube.engine.execute(q)
        return dict(rp.fetchone().items())

    def generate(self):
        """ Generate the resulting records for this query, applying pagination.
        Values will be returned by their reference. """
        if self._limit < 1:
            return
        q = self._get_unpaginated_query()
        if self._offset > 0:
            q = q.offset(self._offset)
        q = q.limit(self._limit)
        rp = self.cube.engine.execute(q)
        while True:
            row = rp.fetchone()
            if row is None:
                return
            yield dict(row.items())
