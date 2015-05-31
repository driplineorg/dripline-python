'''
'''

from __future__ import absolute_import

# standard imports
import threading

# internal imports
from .. import core

__all__ = []


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
        self._run_name = value
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
        self._acquisition_count = 0

    def close_run(self):
        self._run_name = None
        self.run_id = None


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
        self.mantis_queue = mantis_queue

    def start_run(self):
        pass

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

    def close_run(self):
        self._acquisition_count = 0
        super(DAQProvider, self).close_run()
