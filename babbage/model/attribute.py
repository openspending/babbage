from babbage.model.concept import Concept


class Attribute(Concept):
    """ An attribute describes some concrete value stored in the data model.
    This value can either be stored directly on the facts table as a column,
    or introduced via a join. """

    def __init__(self, dimension, name, spec):
        super(Attribute, self).__init__(dimension.model, name, spec)
        self.dimension = dimension

    @property
    def ref(self):
        return '%s.%s' % (self.dimension.hierarchy, self.name)

    def __repr__(self):
        return "<Attribute(%s)>" % self.ref

    def to_dict(self):
        data = self.spec.copy()
        data['ref'] = self.ref
        return data
