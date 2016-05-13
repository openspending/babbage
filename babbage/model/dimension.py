from babbage.model.concept import Concept
from babbage.model.attribute import Attribute


class Dimension(Concept):
    """ A dimension is any property of an entry that can serve to describe
    it beyond its purely numeric ``Measures``. It is defined by several
    attributes, which contain actual values. """

    def __init__(self, model, name, spec, hierarchy=None):
        super(Dimension, self).__init__(model, name, spec)
        self.hierarchy = hierarchy if hierarchy is not None else self.name
        self.join_column_name = spec.get('join_column')

    @property
    def attributes(self):
        for name, attr in self.spec.get('attributes', {}).items():
            yield Attribute(self, name, attr)

    @property
    def label_attribute(self):
        for attr in self.attributes:
            if attr.name == self.spec.get('label_attribute'):
                return attr
        return self.key_attribute

    @property
    def key_attribute(self):
        for attr in self.attributes:
            if attr.name == self.spec.get('key_attribute'):
                return attr

    @property
    def cardinality(self):
        """ Get the number of distinct values of the dimension. This is stored
        in the model as a denormalization which can be generated using a
        method on the ``Cube``. """
        return self.spec.get('cardinality')

    @property
    def cardinality_class(self):
        """ Group the cardinality of the dimension into one of four buckets,
        from very small (less than 5) to very large (more than 1000). """
        if self.cardinality:
            if self.cardinality > 1000:
                return 'high'
            if self.cardinality > 50:
                return 'medium'
            if self.cardinality > 7:
                return 'low'
            return 'tiny'

    @property
    def datatype(self):
        return self.key_attribute.datatype

    def bind(self, cube):
        """ When one column needs to match, use the key. """
        return self.key_attribute.bind(cube)

    def __repr__(self):
        return "<Dimension(%s)>" % self.ref

    def to_dict(self):
        data = self.spec.copy()
        data['ref'] = self.ref
        data['label_attribute'] = self.label_attribute.name
        data['label_ref'] = self.label_attribute.ref
        data['key_attribute'] = self.key_attribute.name
        data['key_ref'] = self.key_attribute.ref
        data['cardinality_class'] = self.cardinality_class
        data['attributes'] = {a.name: a.to_dict() for a in self.attributes}
        data['hierarchy'] = self.hierarchy
        return data
