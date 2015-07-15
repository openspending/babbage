from babbage.exc import BindingException


class Concept(object):
    """ A concept describes any branch of the model: dimensions, attributes,
    measures. """

    def __init__(self, model, name, spec):
        self.model = model
        self.name = name
        self.spec = spec
        self.label = spec.get('label', name)
        self.description = spec.get('description')
        self.column_name = spec.get('column')

    @property
    def ref(self):
        """ A unique reference within the context of this model. """
        return self.name

    def _physical_column(self, cube, column_name):
        """ Return the SQLAlchemy Column object matching a given, possibly
        qualified, column name (i.e.: 'table.column'). If no table is named,
        the fact table is assumed. """
        table_name = self.model.fact_table_name
        if '.' in column_name:
            table_name, column_name = column_name.split('.', 1)
        table = cube._load_table(table_name)
        if column_name not in table.columns:
            raise BindingException('Column does not exist: %r' % column_name,
                                   table=table_name, column=column_name)
        return table, table.columns[column_name]

    def bind_one(self, cube):
        """ Map a model reference to an physical column in the database. """
        table, column = self._physical_column(cube, self.column_name)
        column = column.label(self.ref)
        column.quote = True
        return table, column

    def bind_many(self, cube):
        """ In the special case of projecting a dimension, we want to get all
        matching columns (i.e. all attributes). """
        return [self.bind_one(cube)]

    def __eq__(self, other):
        """ Test concept equality by means of references. """
        if hasattr(other, 'ref'):
            return other.ref == self.ref
        return self.ref == other

    def __unicode__(self):
        return self.ref
