
class Concept(object):
    """ A concept describes any branch of the model: dimensions, attributes,
    measures. """

    def __init__(self, model, name, spec):
        self.model = model
        self.name = name
        self.spec = spec
        self.label = spec.get('label', name)
        self.description = spec.get('description')

    @property
    def ref(self):
        """ A unique reference within the context of this model. """
        return self.name

    def __eq__(self, other):
        """ Test concept equality by means of references. """
        if hasattr(other, 'ref'):
            return other.ref == self.ref
        return self.ref == other

    def __unicode__(self):
        return self.ref
