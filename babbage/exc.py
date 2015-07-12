
class BabbageException(Exception):
    """ A stub exception class for all errors stemming from babbage calls. """

    def __init__(self, message, **context):
        self.message = message
        self.context = context


class BindingException(BabbageException):
    """ A class of exceptions that occur when the bindings between the logical
    model and the physical schema aren't valid. """

    def __init__(self, message, table=None, column=None):
        super(BindingException, self).__init__(message, table=table,
                                               column=column)
