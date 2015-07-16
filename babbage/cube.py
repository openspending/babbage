from sqlalchemy import MetaData
from sqlalchemy.schema import Table

from babbage.model import Model
from babbage.query import Query
from babbage.exc import BindingException
from babbage.model.dimension import Dimension


class Cube(object):
    """ A dataset that can be queried across a set of dimensions and measures.
    This functions as the central hub of functionality for accessing any
    data and queries. """

    def __init__(self, engine, name, model):
        self.name = name
        if not isinstance(model, Model):
            model = Model(model)
        self.model = model
        self.engine = engine
        self.meta = MetaData(bind=engine)

    def _load_table(self, name):
        """ Reflect a given table from the database. """
        if not self.engine.has_table(name):
            raise BindingException('Table does not exist: %r' % name,
                                   table=name)
        return Table(name, self.meta, autoload=True)

    @property
    def _fact_pk(self):
        """ Try to determine the primary key of the fact table for use in
        fact table counting. """
        keys = [c for c in self._fact_table.columns if c.primary_key]
        if len(keys) != 1:
            raise BindingException('Fact table has no single OK: %r' %
                                   self.model.fact_table_name,
                                   table=self.model.fact_table_name)
        return keys[0]

    @property
    def _fact_table(self):
        return self._load_table(self.model.fact_table_name)

    def aggregate(self, aggregates=None, drilldowns=None, cuts=None,
                  order=None, page=None, page_size=None):
        """ Main aggregation function. This is used to compute a given set of
        aggregates, grouped by a given set of drilldown dimensions (i.e.
        dividers). The query can also be filtered and sorted. """
        query = Query(self, distinct=True)
        query.aggregate(aggregates)
        query.cut(cuts)

        summary = query.summary()

        query.drilldown(drilldowns)
        query.order(order)
        query.paginate(page, page_size)
        return {
            'total_cell_count': query.count(),
            'cells': list(query.generate()),
            'summary': summary
        }

    def members(self, ref, cuts=None, order=None, page=None, page_size=None):
        """ List all the distinct members of the given reference, filtered and
        paginated. If the reference describes a dimension, all attributes are
        returned. """
        query = Query(self, distinct=True)
        query.project(ref)
        query.cut(cuts)
        query.order(order)
        query.paginate(page, page_size)
        return {
            'total_member_count': query.count(),
            'data': list(query.generate())
        }

    def facts(self, refs=None, cuts=None, order=None, page=None,
              page_size=None):
        """ List all facts in the cube, returning only the specified references
        if these are specified. """
        query = Query(self)
        query.project(refs)
        query.cut(cuts)
        query.order(order)
        query.paginate(page, page_size)
        return {
            'total_fact_count': query.count(),
            'data': list(query.generate())
        }

    def __repr__(self):
        return '<Cube(%r)' % self.name
