
class BabbageException(Exception):
    """ A stub exception class for all errors stemming from babbage calls. """
    http_equiv = 500

    def __init__(self, message, **context):
        self.message = message
        self.context = context
        super(BabbageException, self).__init__(message)


class BindingException(BabbageException):
    """ A class of exceptions that occur when the bindings between the logical
    model and the physical schema aren't valid. """

    def __init__(self, message, table=None, column=None):
        super(BindingException, self).__init__(message, table=table,
                                               column=column)


class QueryException(BabbageException):
    """ A class of exceptions that occur when an invalid query is submitted
    or the query cannot be executed. """
    http_equiv = 400
