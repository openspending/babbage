from babbage.model.concept import Concept


class Measure(Concept):
    """ A value on the facts table that can be subject to aggregation,
    and is specific to this one fact. This would typically be some
    financial unit, i.e. the amount associated with the transaction or
    a specific portion thereof (i.e. co-financed amounts). """

    def __init__(self, model, name, spec):
        super(Measure, self).__init__(model, name, spec)
        self.column_name = spec.get('column')
        self.aggregates = spec.get('aggregates', ['sum'])

    @property
    def datatype(self):
        return self.spec.get('type')

    def __repr__(self):
        return "<Measure(%s)>" % self.ref

    def to_dict(self):
        data = self.spec.copy()
        data['ref'] = self.ref
        return data
