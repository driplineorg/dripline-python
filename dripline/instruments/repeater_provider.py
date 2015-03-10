'''
'''
from __future__ import absolute_import

from ..core import Provider, Connection, message, constants


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
        logger.debug('trying to send: {}'.format(to_send))
        request = message.RequestMessage(target=self._repeat_target,
                                         msgop=constants.OP_PROVIDER_SEND,
                                         payload=[to_send]
                                        )
        reply = self._conn.send_request(self._repeat_target, request.to_msgpack())
        result = message.Message.from_msgpack(reply)
        return result.payload
