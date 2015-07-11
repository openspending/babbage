from babbage.model.concept import Concept
from babbage.model.attribute import Attribute


class Dimension(Concept):
    """ A dimension is any property of an entry that can serve to describe
    it beyond its purely numeric ``Measures``. It is defined by several
    attributes, which contain actual values. """

    def __init__(self, model, name, spec):
        super(Dimension, self).__init__(model, name, spec)
        self.cardinality = spec.get('cardinality')

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

    def __repr__(self):
        return "<Dimension(%s)>" % self.ref

    def to_dict(self):
        data = self.spec.copy()
        data['ref'] = self.ref
        data['label_attribute'] = self.label_attribute.name
        data['label_ref'] = self.label_attribute.ref
        data['key_attribute'] = self.key_attribute.name
        data['key_ref'] = self.key_attribute.ref
        data['attributes'] = {a.name: a.to_dict() for a in self.attributes}
        return data
