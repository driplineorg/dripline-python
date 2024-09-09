'''
A service for interfacing with SQL database for storage. It is currently only developed and tested against Postgres,
but should be relatively straight forward to generalize to support other SQL flavors if there is an interest.

Note: services using this module will require sqlalchemy (and assuming we're still using postgresql, psycopg2 as the sqlalchemy backend)
'''

#from __future__ import absolute_import
__all__ = []

# std libraries
import json
import os
import traceback

# 3rd party libraries
#TODO either this should be an actual dependency, or we should move the package into a plugin.
try:
    import sqlalchemy
except ImportError:
    pass
from datetime import datetime
from itertools import groupby
import collections

# local imports
from dripline.core import Service, Endpoint, ThrowReply

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


__all__.append('PostgreSQLInterface')
class PostgreSQLInterface(Service):
    '''
    '''

    def __init__(self, database_name, database_server, auths_file=None, **kwargs):
        '''
        Args:
            database_name (str): name of the 'database' to connect to within the database server
            database_server (str): network resolvable hostname of database server
            auths_file (str): expandable path to an authentications file **Note**, this option is considered temporary and like to be removed in a future version
        '''
        if not 'sqlalchemy' in globals():
            raise ImportError('SQLAlchemy not found, required for PostgreSQLInterface class')
        service_kwargs = {k:v for k,v in kwargs.items() if k in ['config', 'name', 'broker', 'port', 'auth_file', 'make_connection']}
        Service.__init__(self, **service_kwargs)
        if auths_file is not None:
            logger.warning("you have passed an auths file directly to 'PostgreSQLInterface.__init-_', this capability is considered temporary")
            self._auths_file = auths_file
        else:
            logger.warning("auths file is currently required... until the future when we remove it from even being an option")

        self._connect_to_db(database_server, database_name)

    def _connect_to_db(self, database_server, database_name):
        '''
        '''
        logger.debug('Connecting to the db')
        #TODO: this is a massive hack; as soon as scarab supports environment variable substitutions, this should be refactored
        credentials = json.loads(open(os.path.expandvars(os.path.expanduser(self._auths_file))).read())['postgresql']
        engine_str = f'postgresql://{credentials["username"]}:{credentials["password"]}@{database_server}/{database_name}'
        self.engine = sqlalchemy.create_engine(engine_str)
        self.meta = sqlalchemy.MetaData()

    def add_child(self, endpoint):
        Service.add_child(self, endpoint)
        if isinstance(endpoint, SQLTable):
            logger.debug(f'Adding sqlalchemy.Table object for "{endpoint.table_name}" to Endpoint')
            endpoint.table = sqlalchemy.Table(endpoint.table_name, self.meta, autoload_with=self.engine, schema=endpoint.schema)


__all__.append("SQLTable")
class SQLTable(Endpoint):
    '''
    A class for making calls to _insert_with_return
    '''
    def __init__(self, table_name,
                 schema=None,
                 required_insert_names=[],
                 return_col_names=[],
                 optional_insert_names=[],
                 default_insert_values={},
                 *args,
                **kwargs):
        '''
        table_name (str): name of the table within the database
        schema (str): name of the schema where the table is located
        required_insert_names (list): list of names (str||dict) of the table columns which must be included on every requested insert (if dict: keys are 'column' and 'payload_key', if string it is assumed that both are that value)
        return_col_names (list): list of names (str) of columns whose values should be returned on completion of the insert
        optional_insert_names (list): list of names (str||dict) of columns which the user may specify on an insert request, but which may be omitted (if dict: keys are 'column' and 'payload_key', if string it is assumed that both are that value)
        default_insert_values (dict): dictionary of {column_names: values} to serve as defaults when inserting, any values provided explicitly on the insert request will override these values
        '''
        if not 'sqlalchemy' in globals():
            raise ImportError('SQLAlchemy not found, required for SQLTable class')
        Endpoint.__init__(self, *args, **kwargs)
        self.table = None
        self.table_name = table_name
        self.schema = schema
        self._return_names = return_col_names
        self._column_map = {}
        self._required_insert_names = self._ensure_col_key_map(required_insert_names)
        self._optional_insert_names = self._ensure_col_key_map(optional_insert_names)
        self._default_insert_dict = default_insert_values

    def _ensure_col_key_map(self, column_list):
        to_return = []
        for a_col in column_list:
            if isinstance(a_col, str):
                to_return.append({'column': a_col, 'payload_key': a_col})
                self._column_map[a_col] = a_col
            elif isinstance(a_col, dict):
                if not 'column' in a_col or not 'payload_key' in a_col:
                    raise KeyError(f"column insert map <{a_col}> does not contain the required keys, ['column', 'payload_key']")
                to_return.append(a_col)
                self._column_map[a_col['payload_key']] = a_col['column']
            else:
                raise TypeError(f"column info <{a_col}> is not of an expected type")
        return to_return

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
        conn = self.service.engine.connect()
        result = conn.execute(this_select)
        return (result.keys(), [i for i in result])

    def _insert_with_return(self, insert_kv_dict, return_col_names_list):
        try:
            ins = self.table.insert().values(**insert_kv_dict)
            if return_col_names_list:
                ins = ins.returning(*[self.table.c[col_name] for col_name in return_col_names_list])
            conn = self.service.engine.connect()
            insert_result = conn.execute(ins)
            if return_col_names_list:
                return_values = insert_result.first()
            else:
                return_values = []
        except sqlalchemy.exc.IntegrityError as err:
            raise ThrowReply('resource_error', f"database integreity error: '{repr(err)}'")
        except Exception as err:
            logger.critical('received an unexpected SQL error while trying to insert:\n{}'.format(str(ins) % insert_kv_dict))
            logger.info('traceback is:\n{}'.format(traceback.format_exc()))
            return
        return dict(zip(return_col_names_list, return_values))

    def do_insert(self, *args, **kwargs):
        '''
        '''
        # make sure that all provided insert values are expected
        for col in list(kwargs.keys()):
            if not col in self._column_map.keys():
                logger.debug(f'got an unexpected insert column <{col}>')
                kwargs.pop(col)
        # make sure that all required columns are present
        for col in self._required_insert_names:
            if not col['payload_key'] in kwargs.keys():
                raise ThrowReply('service_error_invalid_value', f'a value for <{col}> is required!\ngot: {kwargs}')
        # build the insert dict
        this_insert = self._default_insert_dict.copy()
        this_insert.update({self._column_map[key]:value for key,value in kwargs.items()})
        return_vals = self._insert_with_return(this_insert, self._return_names,)
        return return_vals

