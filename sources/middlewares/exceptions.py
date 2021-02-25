""" Классы исключений для middlewares.
"""


class MiddlewaresError(Exception):
    pass


class InvalidHandlerArgument(MiddlewaresError):
    pass


class InputDataValidationError(MiddlewaresError):
    pass
