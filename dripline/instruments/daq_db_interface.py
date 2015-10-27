'''
A service fo interfacing with the DAQ DB (the run table in particular)

Note: services using this module will require sqlalchemy (and assuming we're still using postgresql, psycopg2 as the sqlalchemy backend)
'''

from __future__ import absolute_import

# std libraries
import json
import os
import types

# 3rd party libraries
try:
    import sqlalchemy
except ImportError:
    print('warning sqlalchmy not found, database support will not be available')
####### the above import really does go here, there should probably be some plugin infrastructure or something to deal with this as an optional feature, for now I'll import elsewhere

# local imports
from ..core import Provider, Endpoint#, fancy_init_doc
from ..core.exceptions import *

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = []

__all__.append('RunDBInterface')
class RunDBInterface(Provider):
    '''
    A not-so-flexible provider for getting run_id values.
    '''
    
    def __init__(self, database_name, database_server, tables, *args, **kwargs):
        '''
        ~Params
            database_name (str): name of the database to connect to
            database_server (str): network resolvable hostname of database server
            tables (list): list of names (str) of tables in the database
        ~Params
        '''
        if isinstance(tables, types.StringType):
            tables = [tables]
        Provider.__init__(self, *args, **kwargs)

        self.tables = {}
        self.connect_to_db(database_server, database_name, tables)

    def connect_to_db(self, database_server, database_name, table_names):
        '''
        '''
        credentials = json.loads(open(os.path.expanduser('~')+'/.project8_authentications.json').read())['postgresql']
        engine_str = 'postgresql://{}:{}@{}/{}'.format(credentials['username'],
                                                       credentials['password'],
                                                       database_server,
                                                       database_name
                                                      )
        engine = sqlalchemy.create_engine(engine_str)
        meta = sqlalchemy.MetaData(engine)
        for table in table_names:
            self.tables[table] = sqlalchemy.Table(table, meta, autoload=True, schema='runs')

    def _insert_with_return(self, table_name, insert_kv_dict, return_col_names_list):
        try:
            ins = self.tables[table_name].insert().values(**insert_kv_dict)
            if return_col_names_list:
                ins = ins.returning(*[self.tables[table_name].c[col_name] for col_name in return_col_names_list])
            insert_result = ins.execute()
            if return_col_names_list:
                return_values = insert_result.first()
            else:
                return_values = []
        except Exception as err:
            if str(err).startswith('(psycopg2.IntegrityError)'):
                raise DriplineDatabaseError(str(err))
            else:
                logger.warning('unknown error while working with sql')
                raise
        return dict(zip(return_col_names_list, return_values))


__all__.append("InsertDBEndpoint")
class InsertDBEndpoint(Endpoint):
    '''
    A class for making calls to _insert_with_return
    '''
    def __init__(self, table_name, required_insert_names,
                 return_col_names=[],
                 optional_insert_names=[],
                 default_insert_values={},
                 *args,
                **kwargs):
        '''
        ~Params
            table_name (str): name of the table to insert to
            required_insert_names (list): list of names (str) of the table columns which must be included on every requested insert
            return_col_names (list): list of names (str) of columns whose values should be returned on completion of the insert
            optional_insert_names (list): list of names (str) of columns which the user may specify on an insert request, but which may be omitted
            default_insert_values (dict): dictionary of {column_names: values} to serve as defaults when inserting, any values provided explicitly on the insert request will override these values
        ~Params
        '''
        Endpoint.__init__(self, *args, **kwargs)

        self._table_name = table_name
        self._return_names = return_col_names
        self._required_insert_names = required_insert_names
        self._optional_insert_names = optional_insert_names
        self._default_insert_dict = default_insert_values

    def do_insert(self, *args, **kwargs):
        '''
        '''
        if not isinstance(self.provider, RunDBInterface):
            raise DriplineInternalError('InsertDBEndpoint must have a RunDBInterface as provider')
        # make sure that all provided insert values are expected
        for col in kwargs.keys():
            if (not col in self._required_insert_names) and (not col in self._optional_insert_names):
                #raise DriplineDatabaseError('not allowed to insert into: {}'.format(col))
                kwargs.pop(col)
        # make sure that all required columns are present
        for col in self._required_insert_names:
            if not col in kwargs.keys():
                raise DriplineDatabaseError('a value for <{}> is required'.format(col))
        # build the insert dict
        this_insert = self._default_insert_dict.copy()
        this_insert.update(kwargs)
        return_vals = self.provider._insert_with_return(self._table_name,
                                                        this_insert,
                                                        self._return_names,
                                                       )
        return return_vals
