'''
Dripline's exception and warning classes, including their associated return codes.
'''


from __future__ import absolute_import

__all__ = [
          ]


class DriplineException(Exception):
    '''Base class for all dripline exceptions.

    Implements the optional result field when raising exceptions; can be used to catch all dripline exception types.
    *Not* intended to be raised directly, you should always be raising a more specific derived class.

    Intended primarily to extended the features of the python Exception class, and to allow all dripline-related exceptions to be caught together (but independent of unrelated exceptions).
    '''
    retcode = None
    def __init__(self, msg, result=None):
        super(DriplineException, self).__init__(msg)
        self.result = result
__all__.append('DriplineException')


class DriplineError(DriplineException):
    '''Base class for errors with dripline

    Base class for all error-type exceptions (retcode >= 100).
    *Not* intended as a generic exception or to be used directly, you should always raise a more specific derived class.
    Note that the multiples of 100 are intended as generic within their class of exception sources.
    New generic exceptions (multiples of 100) or specific exceptions (intermediate values) can be added as needed.

    Intended primarily to facilitate catching and handling Errors independently from Warnings
    '''
    retcode = None
__all__.append('DriplineError')


class DriplineWarning(DriplineException):
    '''Generic dripline warning class

    A generic class for "warning" type exceptions (0 < retcode < 100).
    Used to break an execution block and/or return a non-success (!=0) retcode, when a problem or concern exists, but has been recovered.
    Also useful in debugging as warnings can easily be caught and handled separately from errors (ie, by catching this class).

    May be used as a base class for more specific warning-type exceptions, but may also be raised directly.
    '''
    retcode = 0
__all__.append('DriplineWarning')


class DriplineAMQPError(DriplineError):
    retcode = 100
__all__.append('DriplineAMQPError')


class DriplineAMQPConnectionError(DriplineError):
    retcode = 101
__all__.append('DriplineAMQPConnectionError')


class DriplineAMQPRoutingKeyError(DriplineError):
    retcode = 102
__all__.append('DriplineAMQPRoutingKeyError')


class DriplineHardwareError(DriplineError):
    retcode = 200
__all__.append('DriplineHardwareError')


class DriplineHardwareConnectionError(DriplineError):
    retcode = 201
__all__.append('DriplineHardwareConnectionError')


class DriplineHardwareResponselessError(DriplineError):
    retcode = 202
__all__.append('DriplineHardwareResponselessError')


class DriplineInternalError(DriplineError):
    retcode = 300
__all__.append('DriplineInternalError')


class DriplineNoMessageEncodingError(DriplineError):
    retcode = 301
__all__.append('DriplineNoMessageEncodingError')


class DriplineDecodingError(DriplineError):
    retcode = 302
__all__.append('DriplineDecodingError')


class DriplinePayloadError(DriplineError):
    retcode = 303
__all__.append('DriplinePayloadError')


class DriplineValueError(DriplineError):
    retcode = 304
__all__.append('DriplineValueError')


class DriplineTimeoutError(DriplineError):
    retcode = 305
__all__.append('DriplineTimeoutError')


class DriplineMethodNotSupportedError(DriplineError):
    retcode = 306
__all__.append('DriplineMethodNotSupportedError')

class DriplineAccessDenied(DriplineError):
    retcode = 307
__all__.append('DriplineAccessDenied')

class DriplineInvalidKey(DriplineError):
    retcode = 308
__all__.append('DriplineInvalidKey')

class DriplineDeprecated(DriplineError):
    retcode = 309
__all__.append('DriplineDeprecated')

class DriplineDatabaseError(DriplineError):
    retcode = 400
__all__.append("DriplineDatabaseError")

class DriplineGenericDAQError(DriplineError):
    retcode = 500
__all__.append("DriplineGenericDAQError")

class DriplineDAQNotEnabled(DriplineError):
    retcode = 501
__all__.append("DriplineDAQNotEnabled")

exception_map = {}
for exception in __all__:
    exception_map[locals()[exception].retcode] = locals()[exception]
__all__.append('exception_map')
