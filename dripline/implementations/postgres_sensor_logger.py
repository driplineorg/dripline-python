'''
A Postgres Interface-based logger
'''

from __future__ import absolute_import

# standard libs
import logging

# 3rd party libs
import sqlalchemy

# internal imports
from dripline.core import AlertConsumer
from .postgres_interface import PostgreSQLInterface

__all__ = []
logger = logging.getLogger(__name__)


__all__.append('PostgresSensorLogger')
class PostgresSensorLogger(AlertConsumer, PostgreSQLInterface):
    '''
    An alert consumer which converts alert messages into database insertions.

    The assumption made is that complex logic dealing with organization or structure of the particular database should live in the database itself (possibly in a view, with a trigger, ...) and that here we can simply do an insert.
    '''
    def __init__(self, insertion_table_endpoint_name, **kwargs):
        '''
        '''
        AlertConsumer.__init__(self, add_endpoints_now=False, **kwargs)
        PostgreSQLInterface.__init__(self, **kwargs)

        self.default_insertion_table = insertion_table_endpoint_name

        self.connect_to_db(self.auth)

        self.add_endpoints_from_config()

    # add_endpoint is a mess here because of the diamond inheritance, so let's be explicit
    def add_child(self, endpoint):
        AlertConsumer.add_child(self, endpoint)
        self.add_child_table(endpoint)

    def process_payload(self, a_payload, a_routing_key_data, a_message_timestamp, target_table=None):
        try:
            if target_table is None:
                target_table = self.default_insertion_table
            this_data_table = self.sync_children[target_table]
            # combine data sources
            insert_data = {'timestamp': a_message_timestamp}
            insert_data.update(a_routing_key_data)
            insert_data.update(a_payload.to_python())
            logger.info(f"Inserting to endpoint {target_table}; data are:\n{insert_data}")
            # do the insert
            insert_return = this_data_table.do_insert(**insert_data)
            logger.debug(f"Return from insertion: {insert_return}")
            logger.info("finished processing data")
        except sqlalchemy.exc.SQLAlchemyError as err:
            logger.critical(f'Received SQL error while doing insert: {err}')
        except Exception as err:
            logger.critical(f'An exception was raised while processing a payload to insert: {err}')



__all__.append('PostgresMappedSensorLogger')
class PostgresMappedSensorLogger(PostgresSensorLogger):
    '''
    Add-on to PostgresSensorLogger using traditional database structure with an endpoint_map
    '''
    def __init__(self, sensor_type_map_table, data_tables_dict, **kwargs):
        '''
        Args:
            sensor_type_map_table (str): name of endpoint (table) mapping endpoint names to types
            data_tables (dict): mapping of data type to endpoint (table) names
        * All endpoint names should be accounted between the above
        '''
        # map table supercedes need for insertion table
        if 'insertion_table_endpoint_name' not in kwargs:
            kwargs.update( {'insertion_table_endpoint_name' : None} )
        PostgresSensorLogger.__init__(self, **kwargs)

        # verify table values map to endpoints
        if sensor_type_map_table not in self.sync_children:
            raise ValueError(f'sensor_type_map_table ({sensor_type_map_table}) not in endpoint tables ({self.sync_children.keys()})')
        self._sensor_type_map_table = sensor_type_map_table
        for typekey, data_table in data_tables_dict.items():
            if data_table not in self.sync_children:
                raise ValueError(f'data table target ({data_table}) not in endpoint tables ({self.sync_children.keys()})')
        self._data_tables = data_tables_dict

    def process_payload(self, a_payload, a_routing_key_data, a_message_timestamp):
        '''
        method is wrapped to map data insert into correct table
        '''
        # get the type and table for the sensor
        this_type = self.sync_children[self._sensor_type_map_table].do_select(return_cols=["type"],
                                                                              where_eq_dict=a_routing_key_data)
        logger.debug(f'Map query returned {this_type}')
        # if the key is not contained in the table, generate meaningful error message
        try:
            table_name = self._data_tables[this_type[1][0][0]]
        except IndexError:
            logger.critical(f"{a_routing_key_data} is not in database, see {this_type}")
            return
        logger.info(f'Found {a_routing_key_data} in table {table_name}')

        super().process_payload(a_payload, a_routing_key_data, a_message_timestamp, target_table=table_name)
