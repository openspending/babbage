from babbage.validation import validate_model
from babbage.model.dimension import Dimension
from babbage.model.measure import Measure
from babbage.model.aggregate import Aggregate


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
    def fact_table_name(self):
        return self.spec.get('fact_table')

    @property
    def dimensions(self):
        for name, data in self.spec.get('dimensions', {}).items():
            yield Dimension(self, name, data)

    @property
    def measures(self):
        for name, data in self.spec.get('measures', {}).items():
            yield Measure(self, name, data)

    @property
    def attributes(self):
        for dimension in self.dimensions:
            for attribute in dimension.attributes:
                yield attribute

    @property
    def aggregates(self):
        # TODO: nicer way than hard-coding this?
        yield Aggregate(self, 'Facts', 'count')

        for measure in self.measures:
            for function in measure.aggregates:
                yield Aggregate(self, measure.label, function,
                                measure=measure)

    @property
    def concepts(self):
        """ Return all existing concepts, i.e. dimensions, measures and
        attributes within the model. """
        for measure in self.measures:
            yield measure
        for aggregate in self.aggregates:
            yield aggregate
        for dimension in self.dimensions:
            yield dimension
            for attribute in dimension.attributes:
                yield attribute

    def match(self, ref):
        """ Get all concepts matching this ref. For a dimension, that is all
        its attributes, but not the dimension itself. """
        try:
            concept = self[ref]
            if not isinstance(concept, Dimension):
                return [concept]
            return [a for a in concept.attributes]
        except KeyError:
            return []

    @property
    def exists(self):
        """ Check if the model satisfies the basic conditions for being
        queried, i.e. at least one measure. """
        return len(list(self.measures)) > 0

    def __getitem__(self, ref):
        """ Access a ref (dimension, attribute or measure) by ref. """
        for concept in self.concepts:
            if concept.ref == ref:
                return concept
        raise KeyError()

    def __contains__(self, name):
        """ Check if the given ref exists within the model. """
        try:
            self[name]
            return True
        except KeyError:
            return False

    def __repr__(self):
        return "<Model(%r)>" % self.fact_table_name

    def to_dict(self):
        data = self.spec.copy()
        data['measures'] = {m.name: m.to_dict() for m in self.measures}
        data['dimensions'] = {d.name: d.to_dict() for d in self.dimensions}
        data['aggregates'] = {a.ref: a.to_dict() for a in self.aggregates}
        return data
