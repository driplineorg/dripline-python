'''
A service for monitoring service heartbeats
'''

from __future__ import absolute_import

# standard libs
import logging

import time
from datetime import datetime, timedelta
from enum import Enum
import threading

# internal imports
from dripline.core import AlertConsumer, Endpoint
import scarab

__all__ = []
logger = logging.getLogger(__name__)

__all__.append('HeartbeatTracker')
class HeartbeatTracker(Endpoint):
    '''
    '''
    def __init__(self, service_name, **kwargs):
        '''
        Args:
          service_name (str): Name of the service to be monitored
        '''
        Endpoint.__init__(self, **kwargs)
        self.service_name = service_name
        self.last_timestamp = time.time()
        self.is_active = True
        self.status = HeartbeatTracker.Status.UNKNOWN
    
    def process_heartbeat(self, timestamp):
        '''
        '''
        logger.debug(f'New timestamp for {self.service_name}: {timestamp}')
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
                logger.critical(f'Missing heartbeat: {self.service_name}')
                self.status = HeartbeatTracker.Status.CRITICAL
            else:
                if diff > self.service.warning_threshold_s:
                    # report warning
                    logger.warning(f'Missing heartbeat: {self.service_name}')
                    self.status = HeartbeatTracker.Status.WARNING
                else:
                    logger.debug(f'Heartbeat status ok: {self.service_name}')
                    self.status = HeartbeatTracker.Status.OK
        else:
            # report inactive heartbeat received
            logger.debug(f'Inactive heartbeat: time difference: {diff}')
            self.status = HeartbeatTracker.Status.UNKNOWN
        return {'status': self.status, 'time_since_last_hb': diff}

    class Status(Enum):
        OK = 0
        WARNING = 1
        CRITICAL = 2
        UNKNOWN = -1

__all__.append('HeartbeatMonitor')
class HeartbeatMonitor(AlertConsumer):
    '''
    An alert consumer which listens to heartbeat messages and keeps track of the time since the last was received

    '''
    def __init__(self, 
                 time_between_checks_s=20, 
                 warning_threshold_s=120, 
                 critical_threshold_s=300, 
                 add_unknown_heartbeats=True, 
                 endpoint_name_prefix='hbmon_',
                 **kwargs):
        '''
        Args:
            time_between_checks_s (int): number of seconds between heartbeat status checks
            warning_threshold_s (int): warning threshold for missing heartbeats (in seconds)
            critical_threshold_s (int): critical threshold for missing heartbeats (in seconds)
            add_unknown_heartbeats (bool): whether or not to add a new endpoint if an unknown heartbeat is received
            endpoint_name_prefix (str): prefix added to monitored-service names for hbmon endpoints
        '''
        AlertConsumer.__init__(self, **kwargs)

        # Total sleep time is made of multiple smaller sleeps between checking whether the application is cancelled,
        # assuming that time_between_checks_s is larger than the appproximately 5 seconds between checking whether the application is canclled
        # Sleep time shouldn't be less than time_between_checks_s, so n_sleeps is forced to be 1 or more.
        self.time_between_checks_s = time_between_checks_s
        self.n_sleeps = max(1, round(time_between_checks_s / 5))
        self.sleep_time_s = self.time_between_checks_s / self.n_sleeps
        #logger.warning(f'Time between checks: {self.time_between_checks_s}, n_sleeps: {self.n_sleeps}, sleep_time: {self.sleep_time_s}')

        self.warning_threshold_s = warning_threshold_s
        self.critical_threshold_s = critical_threshold_s
        self.add_unknown_heartbeats = add_unknown_heartbeats
        self.endpoint_name_prefix = endpoint_name_prefix

        # Fill the dictionary mapping monitoring name to service name
        self.monitoring_names = {}
        for an_endpoint in self.sync_children.values():
            try:
                self.monitoring_names[an_endpoint.service_name] = an_endpoint.name
            except Exception as err:
                logger.error(f'Error while attempting to fill monitoring_names: {err}')
        logger.debug(f'Initial set of services monitored:\n{self.monitoring_names}')            

    def run(self):
        monitor_thread = threading.Thread(target=self.monitor_heartbeats)

        monitor_thread.start()

        # Run the standard service in the main thread
        AlertConsumer.run(self)

        monitor_thread.join()

    def monitor_heartbeats(self):
        '''
        Performs heartbeat monitoring
        '''
        while not self.is_canceled():
            try:
                logger.debug('Checking endpoints')
                self.process_report(self.run_checks())

                #logger.debug(f'Sleeping for {self.time_between_checks_s} s')
                for i in range(self.n_sleeps):
                    if self.is_canceled():
                        return
                    time.sleep(self.sleep_time_s)
            except Exception as err:
                logger.error(f'Exception caught in monitor_heartbeats\' outer check: {err}')
                scarab.SignalHandler.cancel_all(1)

    def run_checks(self):
        '''
        Checks all endpoints and collects endpoint names by heartbeat tracker status.
        '''
        report_data = {
            HeartbeatTracker.Status.OK: [], 
            HeartbeatTracker.Status.WARNING: [], 
            HeartbeatTracker.Status.CRITICAL: [], 
            HeartbeatTracker.Status.UNKNOWN: [],
        }
        for an_endpoint in self.sync_children.values():
            try:
                endpoint_report = an_endpoint.check_delay()
                report_data[endpoint_report['status']].append(
                    {
                    'name': an_endpoint.name, 
                    'time_since_last_hb': endpoint_report['time_since_last_hb'],
                    }
                )
            except Exception as err:
                logger.error(f'Unable to get status of endpoint {an_endpoint.name}: {err}')
        return report_data
    
    def process_report(self, report_data):
        '''
        Print out the information from the monitoring report data.

        This function can be overridden to handle the monitoring report differently.
        '''
        logger.info('Heartbeat Monitor Status Check')
        if report_data[HeartbeatTracker.Status.CRITICAL]:
            logger.error('Services with CRITICAL status:')
            for endpoint_data in report_data[HeartbeatTracker.Status.CRITICAL]:
                logger.error(f'\t{endpoint_data['name']} -- TSLH: {timedelta(seconds=endpoint_data['time_since_last_hb'])}')
        if report_data[HeartbeatTracker.Status.WARNING]:
            logger.warning('Services with WARNING status:')
            for endpoint_data in report_data[HeartbeatTracker.Status.WARNING]:
                logger.warning(f'\t{endpoint_data['name']} -- TSLH: {timedelta(seconds=endpoint_data['time_since_last_hb'])}')
        if report_data[HeartbeatTracker.Status.OK]:
            logger.info(f'Services with OK status:')
            for endpoint_data in report_data[HeartbeatTracker.Status.OK]:
                logger.info(f'\t{endpoint_data['name']} -- TSLH: {timedelta(seconds=endpoint_data['time_since_last_hb'])}')
        if report_data[HeartbeatTracker.Status.UNKNOWN]:
            logger.info(f'Services with UNKNOWN status:')
            for endpoint_data in report_data[HeartbeatTracker.Status.UNKNOWN]:
                logger.info(f'\t{endpoint_data['name']} -- TSLH: {timedelta(seconds=endpoint_data['time_since_last_hb'])}')

    def process_payload(self, a_payload, a_routing_key_data, a_message_timestamp):
        service_name = a_routing_key_data['service_name']
        if not service_name in self.monitoring_names:
            logger.warning(f'received unexpected heartbeat;\npayload: {a_payload}\nrouting key data: {a_routing_key_data}\ntimestamp: {a_message_timestamp}')
            if self.add_unknown_heartbeats:
                binding = self.endpoint_name_prefix+service_name
                self.add_child(HeartbeatTracker(service_name=service_name, name=binding))
                self.monitoring_names[service_name] = binding
                logger.debug(f'Started monitoring hearteats from {service_name}')
                logger.warning(f'Heartbeat monitor is currently unable to listen for requests addressed to the endpoints of new heartbeat trackers; You will not be able to send messages to {binding}')
                # We'd like to be able to bind the new end point to the service's connection.
                # However, we're unable to bind while the connection is being listened on.
                # We either need a way to stop the service and restart (at which point it would bind all of the endpoints, including the new one),
                # or we use the endpoint as an asychronous endpoint, in which case we need a way to start its thread (there isn't a separate function in dl-cpp to do this at this point).
                #self.bind_key(self.requests_exchange, binding+'.#')
                #logger.debug(f'Added endpoint for unknown heartbeat from {service_name}')
            return
        
        try:
            self.sync_children[self.monitoring_names[service_name]].process_heartbeat(a_message_timestamp)
        except Exception as err:
            logger.error(f'Unable to handle payload for heartbeat from service {service_name}: {err}')

    def do_get(self):
        return self.run_checks()
    