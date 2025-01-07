'''
A service for monitoring service heartbeats
'''

from __future__ import absolute_import

# standard libs
import logging

import time
from datetime import datetime
from enum import Enum
import threading

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
        Endpoint.__init__(self, **kwargs)
        self.last_timestamp = time.time()
        self.is_active = True
        self.status = HeartbeatTracker.Status.OK
    
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
            if diff > self.service.critical_threshold_s:
                # report critical
                logger.critical(f'Missing heartbeat: {self.name}')
                self.status = HeartbeatTracker.Status.CRITICAL
            else:
                if diff > self.service.warning_threshold_s:
                    # report warning
                    logger.warning(f'Missing heartbeat: {self.name}')
                    self.status = HeartbeatTracker.Status.WARNING
                else:
                    logger.debug(f'Heartbeat status ok: {self.name}')
                    self.status = HeartbeatTracker.Status.OK
        else:
            # report inactive heartbeat received
            logger.debug(f'Inactive heartbeat: time difference: {diff}')

    class Status(Enum):
        OK = 0
        WARNING = 1
        CRITICAL = 2

__all__.append('HeartbeatMonitor')
class HeartbeatMonitor(AlertConsumer):
    '''
    An alert consumer which listens to heartbeat messages and keeps track of the time since the last was received

    '''
    def __init__(self, time_between_checks_s=20, warning_threshold_s=120, critical_threshold_s=300, add_unknown_heartbeats=True, **kwargs):
        '''
        Args:
            time_between_checks_s (int): number of seconds between heartbeat status checks
            warning_threshold_s (int): warning threshold for missing heartbeats (in seconds)
            critical_threshold_s (int): critical threshold for missing heartbeats (in seconds)
            add_unknown_heartbeats (bool): whether or not to add a new endpoint if an unknown heartbeat is received
            socket_timeout (int): number of seconds to wait for a reply from the device before timeout.
        '''
        AlertConsumer.__init__(self, **kwargs)

        # Total sleep time is made of multiple smaller sleeps between checking whether the application is cancelled,
        # assuming that time_between_checks_s is larger than the appproximately 5 seconds between checking whether the application is canclled
        # Sleep time shouldn't be less than time_between_checks_s, so n_sleeps is forced to be 1 or more.
        self.time_between_checks_s = time_between_checks_s
        self.n_sleeps = max(1, round(time_between_checks_s / 5))
        self.sleep_time_s = self.time_between_checks_s / self.n_sleeps
        logger.warning(f'Time between checks: {self.time_between_checks_s}, n_sleeps: {self.n_sleeps}, sleep_time: {self.sleep_time_s}')

        self.warning_threshold_s = warning_threshold_s
        self.critical_threshold_s = critical_threshold_s
        self.add_unknown_heartbeats = add_unknown_heartbeats

    def run(self):
        monitor_thread = threading.Thread(target=self.monitor_heartbeats)

        monitor_thread.start()

        # Run the standard service in the main thread
        AlertConsumer.run(self)

        monitor_thread.join()

    def monitor_heartbeats(self):
        while not self.is_canceled():
            try:
                logger.debug('Checking endpoints')
                self.run_checks()

                logger.debug(f'Sleeping for {self.time_between_checks_s} s')
                for i in range(self.n_sleeps):
                    if self.is_canceled():
                        return
                    time.sleep(self.sleep_time_s)
            except Exception as err:
                logger.error(f'Exception caught in monitor_heartbeats\' outer check: {err}')
                self.cancel(1)

    def run_checks(self):
        for an_endpoint in self.sync_children.values():
            try:
                an_endpoint.check_delay()
            except Exception as err:
                logger.error(f'Unable to get status of endpoint {an_endpoint.name}: {err}')

    def process_payload(self, a_payload, a_routing_key_data, a_message_timestamp):
        service_name = a_routing_key_data['service_name']
        if not service_name in self.sync_children:
            logger.warning(f'received unexpected heartbeat;\npayload: {a_payload}\nrouting key data: {a_routing_key_data}\ntimestamp: {a_message_timestamp}')
            if self.add_unknown_heartbeats:
                self.add_child(HeartbeatTracker(name=service_name))
                logger.debug(f'Added endpoint for unknown heartbeat from {service_name}')
            return
        
        try:
            self.sync_children[service_name].process_heartbeat(a_message_timestamp)
        except Exception as err:
            logger.error(f'Unable to handle payload for heartbeat from service {service_name}: {err}')
