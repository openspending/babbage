from sqlalchemy import MetaData
from sqlalchemy.schema import Table
from sqlalchemy.sql.expression import select

from babbage.model import Model
from babbage.model.dimension import Dimension
from babbage.query import count_results, generate_results, first_result
from babbage.query import Cuts, Drilldowns, Fields, Ordering, Aggregates
from babbage.query import Pagination
from babbage.exc import BindingException


class Cube(object):
    """ A dataset that can be queried across a set of dimensions and measures.
    This functions as the central hub of functionality for accessing any
    data and queries. """

    def __init__(self, engine, name, model, fact_table=None):
        self.name = name
        if not isinstance(model, Model):
            model = Model(model)
        self._tables = {}
        if fact_table is not None:
            self._tables[model.fact_table_name] = fact_table
        self.model = model
        self.engine = engine
        self.meta = MetaData(bind=engine)

    def _load_table(self, name):
        """ Reflect a given table from the database. """
        table = self._tables.get(name, None)
        if table is not None:
            return table
        if not self.engine.has_table(name):
            raise BindingException('Table does not exist: %r' % name,
                                   table=name)
        table = Table(name, self.meta, autoload=True)
        self._tables[name] = table
        return table

    @property
    def fact_pk(self):
        """ Try to determine the primary key of the fact table for use in
        fact table counting. """
        keys = [c for c in self.fact_table.columns if c.primary_key]
        if len(keys) != 1:
            raise BindingException('Fact table has no single PK: %r' %
                                   self.model.fact_table_name,
                                   table=self.model.fact_table_name)
        return keys[0]

    @property
    def fact_table(self):
        return self._load_table(self.model.fact_table_name)

    @property
    def is_postgresql(self):
        """ Enable postgresql-specific extensions. """
        return 'postgresql' == self.engine.dialect.name

    def aggregate(self, aggregates=None, drilldowns=None, cuts=None,
                  order=None, page=None, page_size=None, page_max=None):
        """ Main aggregation function. This is used to compute a given set of
        aggregates, grouped by a given set of drilldown dimensions (i.e.
        dividers). The query can also be filtered and sorted. """
        q = select()
        bindings = []
        cuts, q, bindings = Cuts(self).apply(q, bindings, cuts)

        # Count
        attributes, count_q, count_bindings = Drilldowns(self).apply(
            q,
            bindings,
            drilldowns
        )
        count_q = self.restrict_joins(count_q, count_bindings)
        count = count_results(self, count_q)

        # Summary
        aggregates, q, bindings = Aggregates(self).apply(
            q,
            bindings,
            aggregates
        )
        q = self.restrict_joins(q, bindings)
        summary = first_result(self, q.limit(1))

        # Results
        attributes, q, bindings = Drilldowns(self).apply(
            q,
            bindings,
            drilldowns
        )
        q = self.restrict_joins(q, bindings)

        page, q = Pagination(self).apply(q, page, page_size, page_max)
        ordering, q, bindings = Ordering(self).apply(q, bindings, order)
        q = self.restrict_joins(q, bindings)

        cells = list(generate_results(self, q))

        return {
            'total_cell_count': count,
            'cells': cells,
            'summary': summary,
            'cell': cuts,
            'aggregates': aggregates,
            'attributes': attributes,
            'order': ordering,
            'page': page['page'],
            'page_size': page['page_size']
        }

    def members(self, ref, cuts=None, order=None, page=None, page_size=None):
        """ List all the distinct members of the given reference, filtered and
        paginated. If the reference describes a dimension, all attributes are
        returned. """
        q = select()
        bindings = []
        cuts, q, bindings = Cuts(self).apply(q, bindings, cuts)
        fields, q, bindings = \
            Fields(self).apply(q, bindings, ref, distinct=True)
        ordering, q, bindings = \
            Ordering(self).apply(q, bindings, order, distinct=fields[0])
        q = self.restrict_joins(q, bindings)
        count = count_results(self, q)

        page, q = Pagination(self).apply(q, page, page_size)
        q = self.restrict_joins(q, bindings)
        return {
            'total_member_count': count,
            'data': list(generate_results(self, q)),
            'cell': cuts,
            'fields': fields,
            'order': ordering,
            'page': page['page'],
            'page_size': page['page_size']
        }

    def facts(self, fields=None, cuts=None, order=None, page=None,
              page_size=None, page_max=None):
        """ List all facts in the cube, returning only the specified references
        if these are specified. """
        q = select().select_from(self.fact_table)
        bindings = []
        cuts, q, bindings = Cuts(self).apply(q, bindings, cuts)
        q = self.restrict_joins(q, bindings)
        count = count_results(self, q)

        fields, q, bindings = Fields(self).apply(q, bindings, fields)
        ordering, q, bindings = Ordering(self).apply(q, bindings, order)
        page, q = Pagination(self).apply(q, page, page_size, page_max)
        q = self.restrict_joins(q, bindings)
        return {
            'total_fact_count': count,
            'data': list(generate_results(self, q)),
            'cell': cuts,
            'fields': fields,
            'order': ordering,
            'page': page['page'],
            'page_size': page['page_size']
        }

    def compute_cardinalities(self):
        """ This will count the number of distinct values for each dimension in
        the dataset and add that count to the model so that it can be used as a
        hint by UI components. """
        for dimension in self.model.dimensions:
            result = self.members(dimension.ref, page_size=0)
            dimension.spec['cardinality'] = result.get('total_member_count')

    def restrict_joins(self, q, bindings):
        """
        Restrict the joins across all tables referenced in the database
        query to those specified in the model for the relevant dimensions.
        If a single table is used for the query, no unnecessary joins are
        performed. If more than one table are referenced, this ensures
        their returned rows are connected via the fact table.
        """
        if len(q.froms) == 1:
            return q
        else:
            for binding in bindings:
                if binding.table == self.fact_table:
                    continue
                concept = self.model[binding.ref]
                if isinstance(concept, Dimension):
                    dimension = concept
                else:
                    dimension = concept.dimension
                dimension_table, key_col = dimension.key_attribute.bind(self)
                if binding.table != dimension_table:
                    raise BindingException(
                        'Attributes must be of same table as as their'
                        ' dimension key'
                    )
                try:
                    join_column = self.fact_table.columns[
                        dimension.join_column_name
                    ]
                except KeyError:
                    raise BindingException(
                        "Join column '%s' for %r not in fact table."
                        % (dimension.join_column_name, dimension)
                    )

                q = q.where(join_column == key_col)
        return q

    def __repr__(self):
        return '<Cube(%r)' % self.name
