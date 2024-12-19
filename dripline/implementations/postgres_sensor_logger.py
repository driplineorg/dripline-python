'''
A Postgres Interface-based logger
'''

from __future__ import absolute_import

# standard libs
import logging

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

        self.insertion_table_endpoint_name = insertion_table_endpoint_name

        self.connect_to_db(self.auth)

        self.add_endpoints_from_config()

    # add_endpoint is a mess here because of the diamond inheritance, so let's be explicit
    def add_child(self, endpoint):
        AlertConsumer.add_child(self, endpoint)
        self.add_child_table(endpoint)

    def process_payload(self, a_payload, a_routing_key_data, a_message_timestamp):
        this_data_table = self.sync_children[self.insertion_table_endpoint_name]
        # combine data sources
        insert_data = {'timestamp': a_message_timestamp}
        insert_data.update(a_routing_key_data)
        insert_data.update(a_payload.to_python())
        logger.info(f"Inserting from endpoint {self.insertion_table_endpoint_name}; data are:\n{insert_data}")
        # do the insert
        insert_return = this_data_table.do_insert(**insert_data)
        logger.debug(f"Return from insertion: {insert_return}")
        logger.info("finished processing data")
