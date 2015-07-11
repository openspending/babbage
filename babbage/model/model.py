from babbage.model.dimension import Dimension
from babbage.model.measure import Measure


class Model(object):
    """ The ``Model`` serves as an abstract representation of a cube,
    representing its measures, dimensions and attributes. """

    def __init__(self, spec):
        """ Construct the in-memory object representation of this
        dataset's dimension and measures model.

        This is called upon initialization and deserialization of
        the dataset from the SQLAlchemy store.
        """
        self.spec = spec

    @property
    def dimensions(self):
        for name, data in self.spec.get('dimensions', {}).items():
            yield Dimension(self, name, data)

    @property
    def measures(self):
        for name, data in self.spec.get('measures', {}).items():
            yield Measure(self, name, data)

    @property
    def concepts(self):
        for measure in self.measures:
            yield measure
        for dimension in self.dimensions:
            yield dimension
            for attribute in dimension.attributes:
                yield attribute

    @property
    def exists(self):
        return len(self.axes) > 0

    def __getitem__(self, ref):
        """ Access a ref (dimension, attribute or measure) by ref. """
        for concept in self.concepts:
            if concept.ref == ref:
                return concept
        raise KeyError()

    def __contains__(self, name):
        try:
            self[name]
            return True
        except KeyError:
            return False

    def __repr__(self):
        return "<Model(%r)>" % self.spec.get('name')

    def to_dict(self):
        data = self.spec.copy()
        data['measures'] = {m.name: m.to_dict() for m in self.measures}
        data['dimensions'] = {d.name: d.to_dict() for d in self.dimensions}
        return data
