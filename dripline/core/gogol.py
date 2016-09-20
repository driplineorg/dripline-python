'''
Basic abstraction for binding to the alerts exchange
'''

from __future__ import absolute_import

# standard libs
import logging
import re
import traceback
import uuid

# 3rd party libs
import pika

# internal imports
from . import exceptions
from .message import Message
from .service import Service
from .spimescape import Spimescape
from .utilities import fancy_doc

__all__ = ['Gogol']

logger = logging.getLogger(__name__)


@fancy_doc
class Gogol(Spimescape):
    def __init__(self, exchange='alerts', keys=['#'], name=None, **kwargs):
        '''
        exchange (str): (overrides Service default)
        keys (list): (overrides Service default)

        '''
        logger.debug('Gogol initializing')
        if name is None:
            name = __name__ + '-' + uuid.uuid1().hex[:12]
        Spimescape.__init__(self, exchange=exchange, keys=keys, name=name, **kwargs)

    def this_consume(self, message, basic_deliver=None):
        raise NotImplementedError('you must set this_consume to a valid function')

    def on_alert_message(self, channel, method, properties, message):
        logger.debug('in process_message callback')
        try:
            message_unpacked = Message.from_encoded(message, properties.content_encoding)
            self.this_consume(message_unpacked, method)
        except exceptions.DriplineException as err:
            logger.warning(str(err))
        except Exception as err:
            logger.warning('got an exception:\n{}'.format(str(err)))
            logger.debug('traceback follows:\n{}'.format(traceback.format_exc()))
            raise

    def start(self):
        logger.debug("AlertConsumer consume starting")
        self.run()

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        print('Doing Gogol.on_queue_declareok')
        logger.debug('Binding {} to {} with {}'.format(
                         'alerts', self.name, '#')
                        )
        self._channel.queue_bind(self.on_bindok, self.name, 'alerts', '#')
        Service.on_queue_declareok(self, method_frame)
