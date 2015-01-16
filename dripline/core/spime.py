'''
'''

from __future__ import absolute_import
import logging

from .endpoint import Endpoint
from .data_logger import DataLogger

__all__ = ['Spime',
          ]

logger = logging.getLogger(__name__)


class Spime(Endpoint, DataLogger):
    '''
    '''

    def __init__(self, name, log_interval=0.):
        # DataLogger stuff
        DataLogger.__init__(self, log_interval=log_interval)
        self.get_value = self.on_get
        self.store_value = self.report_log
        # Endpoint stuff
        self.name = name
        self.provider = None

    @staticmethod
    def report_log(value):
        logger.info("Should be logging value: {}".format(value))

    def on_config(self, attribute, value):
        '''
        simple access to setting attributes
        '''
        logger.info('setting attribute')
        setattr(self, attribute, value)
