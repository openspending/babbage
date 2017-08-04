from babbage.exc import BindingException


class Concept(object):
    """ A concept describes any branch of the model: dimensions, attributes,
    measures. """

    def __init__(self, model, name, spec, alias=None):
        self.model = model
        self.name = name
        self.alias = name if alias is None else alias
        self.spec = spec
        self.label = spec.get('label', name)
        self.description = spec.get('description')
        self.column_name = spec.get('column')
        self._matched_ref = None

    @property
    def ref(self):
        """ A unique reference within the context of this model. """
        return self.name

    @property
    def refs(self):
        """ Aliases for this model's ref. """
        return [self.ref, self.alias]

    @property
    def matched_ref(self):
        return self.ref if self._matched_ref is None else self._matched_ref

    @property
    def datatype(self):
        """
        String name of the type of the concept, ie string, integer or date,
        to be overridden by concrete subclasses.
        """
        return None

    def match_ref(self, ref):
        """ Check if the ref matches one the concept's aliases.
            If so, mark the matched ref so that we use it as the column label.
        """
        if ref in self.refs:
            self._matched_ref = ref
            return True
        return False

    def _physical_column(self, cube, column_name):
        """ Return the SQLAlchemy Column object matching a given, possibly
        qualified, column name (i.e.: 'table.column'). If no table is named,
        the fact table is assumed. """
        table_name = self.model.fact_table_name
        if '.' in column_name:
            table_name, column_name = column_name.split('.', 1)
        table = cube._load_table(table_name)
        if column_name not in table.columns:
            raise BindingException('Column %r does not exist on table %r' % (
                                   column_name, table_name), table=table_name,
                                   column=column_name)
        return table, table.columns[column_name]

    def bind(self, cube):
        """ Map a model reference to an physical column in the database. """
        table, column = self._physical_column(cube, self.column_name)
        column = column.label(self.matched_ref)
        column.quote = True
        return table, column

    def __eq__(self, other):
        """ Test concept equality by means of references. """
        if hasattr(other, 'ref'):
            return other.ref == self.ref
        return self.ref == other

    def __unicode__(self):
        return self.ref
