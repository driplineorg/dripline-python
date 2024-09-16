'''
A service for monitoring service heartbeats
'''

from __future__ import absolute_import

# standard libs
import logging

import time
from datetime import datetime

# internal imports
from dripline.core import AlertConsumer, Endpoint

__all__ = []
logger = logging.getLogger(__name__)

__all__.append('HeartbeatTracker')
class HeartbeatTracker(Endpoint):
    '''
    '''
    def __init__(self, **kwargs):
        '''
        '''
        super(HeartbeatTracker, self).__init__(**kwargs)
        self.last_timestamp = time.time()
        self.is_active = True
    
    def process_heartbeat(self, timestamp):
        '''
        '''
        logger.debug(f'New timestamp for {self.name}: {timestamp}')
        dt = datetime.fromisoformat(timestamp)
        posix_time = dt.timestamp()
        logger.debug(f'Time since epoch: {posix_time}')
        self.last_timestamp = posix_time

    def check_delay(self):
        '''
        '''
        diff = time.time() - self.last_timestamp
        if self.is_active:
            if diff > self.parent.critical_threshold_s:
                # report critical
                logger.critical(f'Missing heartbeat: {self.name}')
            else:
                if diff > self.parent.warning_threshold_s:
                    # report warning
                    logger.warning(f'Missing heartbeat: {self.name}')
        else:
            # report inactive heartbeat received
            logger.debug(f'Inactive heartbeat: time difference: {diff}')


__all__.append('HeartbeatMonitor')
class HeartbeatMonitor(AlertConsumer):
    '''
    An alert consumer which listens to heartbeat messages and keeps track of the time since the last was received

    '''
    def __init__(self, time_between_checks_s=60, warning_threshold_s=120, critical_threshold_s=300, **kwargs):
        '''
        '''
        super(HeartbeatMonitor, self).__init__(**kwargs)

        self.time_between_checks_s = time_between_checks_s
        self.warning_threshold_s = warning_threshold_s
        self.critical_threshold_s = critical_threshold_s

    def process_payload(self, a_payload, a_routing_key_data, a_message_timestamp):
        if not a_routing_key_data['service_name'] in self.sync_children:
            logger.warning(f'received unexpected heartbeat;\npayload: {a_payload}\nrouting key data: {a_routing_key_data}\ntimestamp: {a_message_timestamp}')
            return
        
        self.sync_children[a_routing_key_data['service_name']].process_heartbeat(a_message_timestamp)
