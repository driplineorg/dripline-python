'''
A service fo interfacing with the DAQ DB (the run table in particular)

Note: services using this module will require sqlalchemy (and assuming we're still using postgresql, psycopg2 as the sqlalchemy backend)
'''

from __future__ import absolute_import

# std libraries
import types

# 3rd party libraries
import sqlalchemy

# local imports
from ..core import Provider

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = []

__all__.append('RunDBInterface')
class RunDBInterface(Provider):
    '''
    A not-so-flexible provider for getting run_id values.
    '''
    
    def __init__(self, user, password, database_name, database_server, tables, *args, **kwargs):
        '''
        '''
        if isinstance(tables, types.StringType):
            tables = [tables]
        Provider.__init__(self, *args, **kwargs)

        self.tables = {}
        self.connect_to_db(user, password, database_server, database_name, tables)

    def connect_to_db(self, user, password, database_server, database_name, table_names):
        '''
        '''
        engine_str = 'postgresql://{}:{}@{}/{}'.format(user, password, database_server, database_name)
        engine = sqlalchemy.create_engine(engine_str)
        meta = sqlalchemy.MetaData(engine)
        for table in table_names:
            self.tables[table] = sqlalchemy.Table(table, meta, autoload=True, schema='runs')

    def insert_with_return(self, table_name, insert_kv_dict, return_col_names_list):
        try:
            ins = self.tables[table_name].insert().values(**insert_kv_dict)
            ins = ins.returning(*[self.tables[table_name].c[col_name] for col_name in return_col_names_list])
            insert_result = ins.execute()
            return_values = insert_result.first()
        except Exception as err:
            logger.warning('unknown error while working with sql')
            raise
        return dict(zip(return_col_names_list, return_values))

    def create_new_run(self, run_name):
        '''
        insert a new run name and get the run_id
        '''
        insert_dict = {'run_name':run_name}
        try:
            ins = self.run_table.insert().values(**insert_dict)
            ins = ins.returning(run_table.c.run_id)
            insert_result = ins.execute()
            (this_run_id,) = insert_result.first()
        except Exception as err:
            logger.warning('unknown error while working with sql')
            raise
        return this_run_id

