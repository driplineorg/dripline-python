'''
'''

from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

__all__ = ['RSA5106b',
          ]


class RSA5106b(EthernetSCPI):
    '''
    '''

    def start_running(self, id=None):
        '''
        Run whatever sequence of commands are required to actually collect data
        '''
        # should be something to ensure MAT output
        if id is None:
            raise ValueError("a run id must be provided, don't just make one up!!")
        # save setup file
        setup_str = "MMEM:STOR:STAT Y:\{id}\{id}.setup;"
        self.send([setup_str.format(id=id), "*OPC?"])
        # return to triggered mode
        trig_mode_str = 'TRIG:SEQ:STAT 1'
        self.send([trig_mode_str, "*OPC?"])

    def stop_running(self):
        trig_mode_str = 'TRIG:SEQ:STAT 0'
        self.send([trig_mode_str, "*OPC?"])
