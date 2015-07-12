from babbage.model import Model


class Cube(object):
    """ A dataset that can be queried across a set of dimensions and measures.
    This functions as the central hub of functionality for accessing any
    data and queries. """

    def __init__(self, engine, name, model):
        self.name = name
        if not isinstance(model, Model):
            model = Model(model)
        self.model = model
        self.engine = engine

    def __repr__(self):
        return '<Cube(%r)' % self.name
