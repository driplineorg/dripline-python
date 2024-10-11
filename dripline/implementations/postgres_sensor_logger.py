'''
A Postgres Interface-based logger
'''

from __future__ import absolute_import

# standard libs
import logging
import re

from scarab import Authentication

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
        super(PostgresSensorLogger, self).__init__(**kwargs)

        self.insertion_table_endpoint_name = insertion_table_endpoint_name

    # add_endpoint is a mess here because of the diamond inheritance, so let's be explicit
    def add_child(self, endpoint):
        PostgreSQLInterface.add_child(self, endpoint)

    def process_payload(self, a_payload, a_routing_key_data, a_message_timestamp):
        this_data_table = self.sync_children[self.insertion_table_endpoint_name]
        # combine data sources
        insert_data = {'timestamp': a_message_timestamp}
        insert_data.update(a_routing_key_data)
        insert_data.update(a_payload.to_python())
        logger.info(f"insert data are:\n{insert_data}")
        # do the insert
        this_data_table.do_insert(**insert_data)
        logger.info("finished processing data")
