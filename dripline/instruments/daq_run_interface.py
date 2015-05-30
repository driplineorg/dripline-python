'''
'''

from __future__ import absolute_import

# standard imports
import threading

# internal imports
import ..core

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
        self._run_number = None
        self._directory_path = directory_path
        self._run_table_endpoint = run_table_endpoint

    @property
    def run_name(self):
        return self._run_name
    @run_name.setter
    def run_name(self, value):
        self._run_name = value
        # this is where I should get a run_id to go with my run_name
        self._run_number = 0

    def close_run(self):
        self._run_name = None
        self._run_number = None


class MantisProvider(DAQProvider):
    '''
    A DAQProvider for interacting with Mantis DAQ
    '''
    def __init__(self,
                 mantis_queue='mantis',
                 **kwargs
                ):
        DAQProvider.__init__(self, **kwargs)
        self.mantis_queue = mantis_queue
        self._acquisition_count = 0

    def close_run(self):
        self._acquisition_count = 0
        super(DAQProvider, self).close_run()
