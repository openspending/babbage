
class Hierarchy(object):
    """Represents a logical grouping and ordering of existing dimensions"""

    def __init__(self, name, hierarchy):
        self.name = name
        self.label = hierarchy.get('label', name)
        self.levels = hierarchy.get('levels', [])

    def to_dict(self):
        data = dict()
        data['ref'] = self.name
        data['label'] = self.label
        data['levels'] = self.levels[:]
        return data
