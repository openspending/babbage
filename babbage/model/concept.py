
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
        return self.name
