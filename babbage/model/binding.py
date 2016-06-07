class Binding(object):
    def __init__(self, table, ref):
        self.table = table
        self.ref = ref

    def __unicode__(self):
        return u"<Binding(%r, %r)>" % (self.table.name, self.ref)

    def __repr__(self):
        return self.__unicode__()
