'''
A Postgres Interface-based logger
'''

from __future__ import absolute_import

# standard libs
import logging
import re

# internal imports
from dripline.core import AlertConsumer#, exceptions
from .postgres_interface import PostgreSQLInterface

__all__ = []
logger = logging.getLogger(__name__)


__all__.append('PostgresSensorLogger')
class PostgresSensorLogger(AlertConsumer, PostgreSQLInterface):
    '''
    An alert consumer which converts alert messages into database insertions.

    The assumption made is that complex logic dealing with organization or structure of the particular database should live in the database itself (possibly in a view, with a trigger, ...) and that here we can simply do an insert.
    '''
    def __init__(self, inertion_table_endpoint_name, **kwargs):
        '''
        '''
        #self.prefix = sensors_key
        PostgreSQLInterface.__init__(self, **kwargs)
        AlertConsumer.__init__(self, **kwargs)

        self.insertion_table_endpoint_name = insertion_table_endpoint_name
        #self._sensor_type_map_table = sensor_type_map_table
        #self._sensor_type_column_name = sensor_type_column_name
        #self._sensor_type_match_column = sensor_type_match_column
        #self._sensor_types = {}
        #self._data_tables = data_tables_dict
        #self.service = self

    # add_endpoint is a mess here because of the diamond inheritance, so let's be explicit
    def add_child(self, endpoint):
        PostgreSQLInterface.add_endpoint(self, endpoint)

    #def this_consume(self, message, basic_deliver):
    def process_payload(self, a_payload, a_routing_key_data, a_message_timestamp):
        sensor_name = a_routing_key_data['endpoint_name']

        #this_table = self.endpoints[self._sensor_type_map_table]
        #this_type = this_table.do_select(return_cols=[self._sensor_type_column_name],
        #                                 where_eq_dict={self._sensor_type_match_column:sensor_name},
        #                                )
        #self._sensor_types[sensor_name] = this_type[1][0][0]
        #if not self._sensor_types[sensor_name] in self._data_tables:
        #    logger.critical('endpoint with name "{}" is not configured with a recognized type in the sensors_list table'.format(sensor_name))
        #    return
        this_data_table = self.sync_endpoints[self.insertion_table_endpoint_name]

        ### Log the sensor value
        insert_data = {'timestamp': a_message_timestamp}
        insert_data.update(a_routing_key_data)
        insert_data.update(a_payload)
        #insert_data = {'endpoint_name': sensor_name,
        #               'timestamp': a_payload.get('timestamp', a_message_timestamp),
        #              }
        #for key in ['value_raw', 'value_cal', 'memo']:
        #    if key in message.payload:
        #        insert_data[key] = message.payload[key]
        this_data_table.do_insert(**insert_data)
        logger.info('value logged for <{}>'.format(sensor_name))
