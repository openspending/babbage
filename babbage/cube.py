from sqlalchemy import MetaData
from sqlalchemy.schema import Table

from babbage.model import Model
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

    def map(self, ref):
        """ Map a model reference to an physical column in the database. """
        concept = self.model[ref]
        if isinstance(concept, Dimension):
            concept = concept.key_attribute
        return self._physical_column(concept.column_name)

    def _physical_column(self, column_name):
        """ Return the SQLAlchemy Column object matching a given, possibly
        qualified, column name (i.e.: 'table.column'). If no table is named,
        the fact table is assumed. """
        table_name = self.model.fact_table_name
        if '.' in column_name:
            table_name, column_name = column_name.split('.', 1)
        table = self._load_table(table_name)
        if column_name not in table.columns:
            raise BindingException('Column does not exist: %r' % column_name,
                                   table=table_name, column=column_name)
        return table.columns[column_name]

    # mock API (to be implemented):
    def aggregate(self):
        pass

    def members(self, ref):
        pass

    def facts(self):
        pass

    def __repr__(self):
        return '<Cube(%r)' % self.name
