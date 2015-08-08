'''
'''
from __future__ import absolute_import

import types

from ..core import Provider, message, constants, exceptions, exception_map


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
        self._broker_info = broker

    def send_request(self, target, request):
        result = self.portal.send_request(self._repeat_target, request)
        if not 'retcode' in result:
            raise core.exceptions.DriplineInternalError('no return code in reply')
        if not result.retcode == 0:
            msg = ''
            if 'ret_msg' in result.payload:
                msg = result.payload['ret_msg']
            raise exception_map[result.retcode](msg)
        return result.payload

    def send(self, to_send):
        to_send = {'values':to_send}
        logger.debug('trying to send: {}'.format(to_send))
        request = message.RequestMessage(msgop=constants.OP_SEND,
                                         payload=to_send,
                                        )
        return self.send_request(self._repeat_target, request)

    def on_get(self):
        payload = {'values':[]}
        request = message.RequestMessage(msgop=constants.OP_GET, payload=payload)
        return self.send_request(self._repeat_target, request)

    def on_set(self, value):
        payload = {'values':[value]}
        request = message.RequestMessage(msgop=constants.OP_SET, payload=payload)
        return self.send_request(self._repeat_target, request)

    def on_config(self, attribute, value=None):
        payload = {'values': [attribute]}
        if value is not None:
            payload['values'].append(value)
        request = message.RequestMessage(msgop=constants.OP_CONFIG, payload=payload)
        return self.send_request(self._repeat_target, request)
