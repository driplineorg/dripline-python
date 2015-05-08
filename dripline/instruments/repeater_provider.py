'''
'''
from __future__ import absolute_import

import types

from ..core import Provider, Connection, message, constants, exception_map


import logging
logger = logging.getLogger(__name__)

__all__ = ['RepeaterProvider',
          ]

class RepeaterProvider(Provider):
    
    def __init__(self,
                 repeat_target,
                 broker,
                 **kwargs):
        Provider.__init__(self, **kwargs)
        self._repeat_target = repeat_target
        self._conn = Connection(broker)

    def send(self, to_send):
        to_send = {'values':[to_send]}
        logger.debug('trying to send: {}'.format(to_send))
        request = message.RequestMessage(msgop=constants.OP_SEND,
                                         payload=to_send,
                                        )
        reply = self._conn.send_request(self._repeat_target, request.to_msgpack())
        result = message.Message.from_msgpack(reply)
        if not result.retcode == 0:
            msg = ''
            if 'ret_msg' in result.payload:
                msg = result.payload['ret_msg']
            raise exception_map[result.retcode](msg)
        return result.payload
