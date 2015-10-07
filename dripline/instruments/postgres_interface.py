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

# local imports
from ..core import Provider, Endpoint, fancy_doc
from ..core.exceptions import *

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = []

__all__.append('PostgreSQLInterface')
@fancy_doc
class PostgreSQLInterface(Provider):
    '''
    A not-so-flexible provider for getting run_id values.
    '''
    
    def __init__(self, database_name, database_server, **kwargs):
        '''
        database_name (str): name of the database to connect to
        database_server (str): network resolvable hostname of database server
        '''
        Provider.__init__(self, **kwargs)
        self._connect_to_db(database_server, database_name)

    def _connect_to_db(self, database_server, database_name):
        '''
        '''
        credentials = json.loads(open(os.path.expanduser('~')+'/.project8_authentications.json').read())['postgresql']
        engine_str = 'postgresql://{}:{}@{}/{}'.format(credentials['username'],
                                                       credentials['password'],
                                                       database_server,
                                                       database_name
                                                      )
        self.engine = sqlalchemy.create_engine(engine_str)
        self.meta = sqlalchemy.MetaData(self.engine)

    def add_endpoint(self, endpoint):
        Provider.add_endpoint(self, endpoint)
        if isinstance(endpoint, SQLTable):
            endpoint.table = sqlalchemy.Table(endpoint.table_name, self.meta, autoload=True, schema=endpoint.schema)


__all__.append("SQLTable")
@fancy_doc
class SQLTable(Endpoint):
    '''
    A class for making calls to _insert_with_return
    '''
    def __init__(self, table_name, schema,
                 required_insert_names=None,
                 return_col_names=[],
                 optional_insert_names=[],
                 default_insert_values={},
                 *args,
                **kwargs):
        '''
        table_name (str): name of the table within the database
        schema (str): name of the schema where the table is located
        required_insert_names (list): list of names (str) of the table columns which must be included on every requested insert
        return_col_names (list): list of names (str) of columns whose values should be returned on completion of the insert
        optional_insert_names (list): list of names (str) of columns which the user may specify on an insert request, but which may be omitted
        default_insert_values (dict): dictionary of {column_names: values} to serve as defaults when inserting, any values provided explicitly on the insert request will override these values
        '''
        Endpoint.__init__(self, *args, **kwargs)

        self.table = None
        self.table_name = table_name
        self.schema = schema
        self._return_names = return_col_names
        self._required_insert_names = required_insert_names
        self._optional_insert_names = optional_insert_names
        self._default_insert_dict = default_insert_values

    def do_select(self, return_cols=[], where_eq_dict={}, where_lt_dict={}, where_gt_dict={}):
        '''
        return_cols (list of str): string names of columns, internally converted to sql reference; if evaluates as false, all columns are returned
        where_eq_dict (dict): keys are column names (str), and values are tested with '==' 
        where_lt_dict (dict): keys are column names (str), and values are tested with '<'
        where_gt_dict (dict): keys are column names (str), and values are tested with '>'
        
        Other select "where" statements are not supported

        Returns: a tuple, 1st element is list of column names, 2nd is a list of tuples of the rows that matched the select
        '''
        if not return_cols:
            return_cols = self.table.c
        else:
            return_cols = [sqlalchemy.text(col) for col in return_cols]
        this_select = sqlalchemy.select(return_cols)
        for c,v in where_eq_dict.items():
            this_select = this_select.where(getattr(self.table.c,c)==v)
        for c,v in where_lt_dict.items():
            this_select = this_select.where(getattr(self.table.c,c)<v)
        for c,v in where_gt_dict.items():
            this_select = this_select.where(getattr(self.table.c,c)>v)
        result = self.provider.engine.execute(this_select)
        return (result.keys(), [i for i in result])

    def _insert_with_return(self, insert_kv_dict, return_col_names_list):
        try:
            ins = self.table.insert().values(**insert_kv_dict)
            if return_col_names_list:
                ins = ins.returning(*[self.table.c[col_name] for col_name in return_col_names_list])
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

    def do_insert(self, *args, **kwargs):
        '''
        '''
        if not isinstance(self.provider, PostgreSQLInterface):
            raise DriplineInternalError('InsertDBEndpoint must have a RunDBInterface as provider')
        # make sure that all provided insert values are expected
        for col in kwargs.keys():
            if (not col in self._required_insert_names) and (not col in self._optional_insert_names):
                #raise DriplineDatabaseError('not allowed to insert into: {}'.format(col))
                logger.warning('got an unexpected insert column <{}>'.format(col))
                kwargs.pop(col)
        # make sure that all required columns are present
        for col in self._required_insert_names:
            if not col in kwargs.keys():
                raise DriplineDatabaseError('a value for <{}> is required'.format(col))
        # build the insert dict
        this_insert = self._default_insert_dict.copy()
        this_insert.update(kwargs)
        return_vals = self._insert_with_return(this_insert,
                                               self._return_names,
                                              )
        return return_vals
