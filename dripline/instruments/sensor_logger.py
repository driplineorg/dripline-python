'''
sensor logger now as a service
'''

from __future__ import absolute_import

# standard libs
import logging
import re

# internal imports
from ..core import Gogol, exceptions
from .postgres_interface import PostgreSQLInterface

__all__ = []
logger = logging.getLogger(__name__)


__all__.append('SensorLogger')
class SensorLogger(Gogol, PostgreSQLInterface):
    '''
    Project 8 slow control table implementation
    '''
    def __init__(self, sensor_type_map_table, data_tables_dict={}, **kwargs):
        '''
        sensor_type_map_table (str): name of the child endpoint of this instance which provides access to the endpoint_id_map, which stores the sensor type
        data_tables_dict (dict): dictionary mapping types (in the sensor_type_map_table) to child endpoints of this instance which provide access to the data_table for that type
        '''
        Gogol.__init__(self, **kwargs)
        PostgreSQLInterface.__init__(self, **kwargs)

        self._sensor_type_map_table = sensor_type_map_table
        self._sensor_types = {}
        self._data_tables = data_tables_dict

    def this_consume(self, message, basic_deliver):
        ### Get the sensor name
        sensor_name = None
        if '.' in basic_deliver.routing_key:
            re_out = re.match(r'sensor_value.(?P<from>\S+)', basic_deliver.routing_key)
            sensor_name = re_out.groupdict()['from']
        # note that the following is deprecated in dripline 2.x, retained for compatibility
        elif 'from' in message['payload']: 
            sensor_name = message['payload']['from']
        else:
            raise exceptions.DriplineValueError('unknown sensor name')
        
        ### Get the type and table for the sensor
        this_type = None
        if sensor_name not in self._sensor_types.keys():
            this_table = self.endpoints[self._sensor_type_map_table]
            this_type = this_table.do_select(return_cols=['type'],
                                             where_eq_dict={'endpoint_name':sensor_name},
                                            )
            self._sensor_types[sensor_name] = this_type[1][0][0]
        this_data_table = self.endpoints[self._data_tables[self._sensor_types[sensor_name]]]
        
        ### Log the sensor value
        insert_data = {'endpoint_name': sensor_name,
                       'timestamp': message['timestamp'],
                      }
        for key in ['value_raw', 'value_cal', 'memo']:
            if key in message.payload:
                insert_data[key] = message.payload[key]
        this_data_table.do_insert(**insert_data)
        logger.info('value logged for <{}>'.format(sensor_name))
