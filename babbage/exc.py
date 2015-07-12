
class BabbageException(Exception):
    """ A stub exception class for all errors stemming from babbage calls. """

    def __init__(self, message):
        self.message = message
