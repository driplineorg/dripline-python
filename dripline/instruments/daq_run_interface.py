'''
'''

from __future__ import absolute_import

# standard imports
import logging
import threading

# internal imports
from .. import core

__all__ = []

logger = logging.getLogger(__name__)

__all__.append('DAQProvider')
class DAQProvider(core.Provider):
    '''
    Base class for providing a uniform interface to different DAQ systems
    '''
    def __init__(self,
                 daq_name,
                 run_table_endpoint,
                 directory_path,
                 **kwargs):
        '''
        '''
        core.Provider.__init__(self, **kwargs)

        self.stop_thread = threading.Timer(0, self.end_run, ())
        self.daq_name = daq_name
        self._run_name = None
        self.run_id = None
        self.directory_path = directory_path
        self.run_table_endpoint = run_table_endpoint
        self._acquisition_count = None

    @property
    def run_name(self):
        return self._run_name
    @run_name.setter
    def run_name(self, value):
        _conn = core.Connection(self.portal.broker)
        request = core.RequestMessage(msgop=core.OP_CMD,
                                      payload={'values':['do_insert'],
                                               'run_name':value,
                                              },
                                     )
        result = _conn.send_request(self.run_table_endpoint,
                                    request=request,
                                    decode=True,
                                   )
        self.run_id = result.payload['run_id']
        self._run_name = value
        self._acquisition_count = 0

    def end_run(self):
        run_was = self.run_id
        if self.stop_thread.is_alive():
            self.stop_thread.cancel()
        self._run_name = None
        self.run_id = None
        logger.info('run <{}> ended'.format(run_was))
    
    def start_run(self, run_name):
        '''
        '''
        self.run_name = run_name
    
    def start_timed_run(self, run_name, run_time):
        '''
        '''
        self.stop_thread = threading.Timer(float(run_time), # log interval [seconds]
                                           self.end_run, # function to call
                                           (), # args tuple
                                          )
        self.start_run(run_name)
        self.stop_thread.start()


__all__.append('MantisProvider')
class MantisProvider(DAQProvider, core.Spime):
    '''
    A DAQProvider for interacting with Mantis DAQ
    '''
    def __init__(self,
                 mantis_queue='mantis',
                 **kwargs
                ):
        DAQProvider.__init__(self, **kwargs)
        core.Spime.__init__(self, **kwargs)
        self.alert_routing_key = 'daq_requests'
        self.mantis_queue = mantis_queue

    def start_run(self, run_name):
        super(MantisProvider, self).start_run(run_name)
        self.logging_status = 'on'

    def on_get(self):
        '''
        Setting an on_get so that the logging functionality can be used to queue multiple acquisitions.
        '''
        if self.run_id is None:
            raise core.DriplineInternalError('run number is None, must request a run_id assignment prior to starting acquisition')
        _conn = core.Connection(self.portal.broker)
        filepath = '{}/{:09d}_{:09d}.egg'.format(self.directory_path,
                                         self.run_id,
                                         self._acquisition_count)
        request = core.RequestMessage(payload={'values':[], 'file':filepath},
                                      msgop=core.OP_RUN,
                                     )
        result = _conn.send_request(self.mantis_queue,
                                    request=request,
                                    decode=True,
                                   )
        if not result.retcode == 0:
            msg = ''
            if 'ret_msg' in result.payload:
                msg = result.payload['ret_msg']
            logger.warning('got an error from mantis: {}'.format(msg))
        else:
            self._acquisition_count += 1
            return "acquisition of [{}] requested".format(filepath)

    def end_run(self):
        self._loop_process.cancel()
        if self.logging_status == 'started':
            self.logging_status = 'off'
        super(MantisProvider, self).end_run()
        self._acquisition_count = 0
