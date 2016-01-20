'''
Dripline's exception and warning classes, including their associated return codes.
'''


from __future__ import absolute_import

__all__ = [
          ]


class DriplineException(Exception):
    retcode = None
    def __init__(self, msg, result=None):
        super(DriplineException, self).__init__(msg)
        self.result = result
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

exception_map = {}
for exception in __all__:
    exception_map[locals()[exception].retcode] = locals()[exception]
__all__.append('exception_map')
