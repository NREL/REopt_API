class Error(Exception):
    """Base class for exceptions in this module"""
    pass


class SubprocessTimeoutError(Error):
    """ Exception raised when a subprocess times out

    Attributes:
        message - explanation of the error
    """

    def __init__(self, message):
        self.message = message

