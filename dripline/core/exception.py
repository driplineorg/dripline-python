'''
Dripline's exception and warning classes
'''


from __future__ import absolute_import

__all__ = [
          ]


class DriplineException(Exception):
    retcode = None
__all__.append('DriplineException')


class DriplineError(DriplineException):
    retcode = None
__all__.append('DriplineError')


class DriplineWarning(DriplineException):
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
