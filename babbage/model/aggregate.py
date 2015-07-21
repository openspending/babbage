from sqlalchemy import func

from babbage.model.concept import Concept


class Aggregate(Concept):
    """ An aggregates describes the application of an agggregate function (such
    as summing, averages, counts etc.) to a measure or the primary key of the
    cube. """

    def __init__(self, model, label, function, measure=None):
        super(Aggregate, self).__init__(model, None, {'label': label})
        self.function = function
        self.measure = measure

    @property
    def ref(self):
        if self.measure is not None:
            return '%s.%s' % (self.measure.ref, self.function)
        return '_%s' % self.function

    def bind(self, cube):
        """ When one column needs to match, use the key. """
        if self.measure:
            table, column = self.measure.bind(cube)
        else:
            table, column = cube.fact_table, cube.fact_pk
        # apply the SQL aggregation function:
        column = getattr(func, self.function)(column)
        column = column.label(self.ref)
        column.quote = True
        return table, column

    def __repr__(self):
        return "<Aggregate(%s)>" % self.ref

    def to_dict(self):
        data = self.spec.copy()
        data['ref'] = self.ref
        data['function'] = self.function
        if self.measure is not None:
            data['measure'] = self.measure.ref
        return data
