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
#import types
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
#import six

# local imports
#from dripline.core import Provider, Endpoint, fancy_doc, constants
from dripline.core import Service, Endpoint
#from dripline.core.exceptions import *

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#__all__.append('SQLSnapshot')

__all__.append('PostgreSQLInterface')
class PostgreSQLInterface(Service):
    '''
    '''

    def __init__(self, database_name, database_server, auths_file=None, **kwargs):
        '''
        database_name (str): name of the 'database' to connect to within the database server
        database_server (str): network resolvable hostname of database server
        auths_file (str): expandable path to an authentications file **Note, this option is considered temporary and like to be removed in a future version
        '''
        if not 'sqlalchemy' in globals():
            raise ImportError('SQLAlchemy not found, required for PostgreSQLInterface class')
        Service.__init__(self, **kwargs)
        self._connect_to_db(database_server, database_name)
        self._endpoint_name_set = set()
        if auths_file is not None:
            logger.warning("you have passed an auths file directly to 'PostgreSQLInterface.__init-_', this capability is considered temporary")
            self._auths_file = auths_file
        else:
            logger.warning("auths file is currently required... until the future when we remove it from even being an option")

    def _connect_to_db(self, database_server, database_name):
        '''
        '''
        logger.debug('Connecting to the db')
        #TODO: this is a massive hack; as soon as scarab supports environment variable substitutions, this should be refactored
        credentials = json.loads(open(os.path.expandvars(os.path.expanduser(self._auths_file))).read())['postgresql']
        engine_str = 'postgresql://{}:{}@{}/{}'.format(credentials['username'],
                                                       credentials['password'],
                                                       database_server,
                                                       database_name
                                                      )
        self.engine = sqlalchemy.create_engine(engine_str)
        self.meta = sqlalchemy.MetaData(self.engine)

    def add_child(self, endpoint):
        Service.add_child(self, endpoint)
        if isinstance(endpoint, SQLTable):
            logger.debug('Adding sqlalchemy.Table object for "{}" to Endpoint'.format(endpoint.table_name))
            endpoint.table = sqlalchemy.Table(endpoint.table_name, self.meta, autoload=True, schema=endpoint.schema)


__all__.append("SQLTable")
class SQLTable(Endpoint):
    '''
    A class for making calls to _insert_with_return
    '''
    def __init__(self, table_name, schema,
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
                    raise KeyError("column insert map <{}> does not contain the required keys, ['column', 'payload_key']".format(a_col))
                to_return.append(a_col)
                self._column_map[a_col['payload_key']] = a_col['column']
            else:
                raise TypeError("column info <{}> is not of an expected type".format(a_col))
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
        except sqlalchemy.exc.IntegrityError as err:
            raise DriplineDatabaseError(err)
        except Exception as err:
            logger.critical('received an unexpected SQL error while trying to insert:\n{}'.format(str(ins) % insert_kv_dict))
            logger.info('traceback is:\n{}'.format(traceback.format_exc()))
            return
        return dict(zip(return_col_names_list, return_values))

    def do_insert(self, *args, **kwargs):
        '''
        '''
        if not isinstance(self.provider, PostgreSQLInterface):
            raise DriplineInternalError('InsertDBEndpoint must have a RunDBInterface as provider')
        # make sure that all provided insert values are expected
        for col in kwargs.keys():
            if not col in self._column_map.keys():
                #raise DriplineDatabaseError('not allowed to insert into: {}'.format(col))
                logger.warning('got an unexpected insert column <{}>'.format(col))
                kwargs.pop(col)
        # make sure that all required columns are present
        for col in self._required_insert_names:
            if not col['payload_key'] in kwargs.keys():
                raise DriplineDatabaseError('a value for <{}> is required!\ngot: {}'.format(col, kwargs))
        # build the insert dict
        this_insert = self._default_insert_dict.copy()
        this_insert.update({self._column_map[key]:value for key,value in kwargs.items()})
        return_vals = self._insert_with_return(this_insert, self._return_names,)
        return return_vals

#@fancy_doc
#class SQLSnapshot(SQLTable):
#
#    def __init__(self, target_items, payload_field='value_cal', *args, **kwargs):
#        '''
#        target_items (list): items (str) to take snapshot of
#        payload_field (str): field to take from database instead of value_cal
#        '''
#        if not 'sqlalchemy' in globals():
#            raise ImportError('SQLAlchemy not found, required for SQLSnapshot class')
#        SQLTable.__init__(self, *args, **kwargs)
#        self.target_items = target_items
#        self.payload_field = payload_field
#
#    def get_logs(self, start_timestamp, end_timestamp):
#        '''
#        Method to retrieve all database values for all endpoints between two timestamps.  Used as part of standard DAQ operation
#        Both input timestamps must be follow the format of constants.TIME_FORMAT, i.e. YYYY-MM-DDThh:mm:ssZ
#        start_timestamp (str): oldest timestamp for query into database
#        ending_timesamp (str): most recent timestamp for query into database
#        '''
#        start_timestamp = str(start_timestamp)
#        end_timestamp = str(end_timestamp)
#
#        # Parsing timestamps
#        self._try_parsing_date(start_timestamp)
#        self._try_parsing_date(end_timestamp)
#        if not end_timestamp > start_timestamp:
#            raise DriplineValueError('end_timestamp ("{}") must be > start_timestamp ("{}")!'.format(end_timestamp,start_timestamp))
#
#        # Connect to id map table + assign alises
#        self._connect_id_table()
#        t = self.table.alias()
#        id_t = self.it.alias()
#
#        # Select query + result
#        s = sqlalchemy.select([id_t.c.endpoint_name,t.c.timestamp,t.c.value_raw,t.c.value_cal]).select_from(t.join(id_t,t.c.endpoint_id == id_t.c.endpoint_id))
#        logger.debug('querying database for entries between "{}" and "{}"'.format(start_timestamp,end_timestamp))
#        s = s.where(sqlalchemy.and_(t.c.timestamp>=start_timestamp,t.c.timestamp<=end_timestamp)).order_by(id_t.c.endpoint_name.asc())
#        try:
#            query_return = self.provider.engine.execute(s).fetchall()
#        except DriplineDatabaseError as dripline_error:
#            logger.error('{}; in executing SQLAlchemy select statement'.format(dripline_error.message))
#            return
#        if not query_return:
#            logger.info('returning empty record')
#            return {'value_raw': {}}
#
#        # Counting how many times each endpoint is present
#        endpoint_name_raw = []
#        endpoint_dict = {}
#        for row in query_return:
#            endpoint_name_raw.append(str(row['endpoint_name']))
#        for key,group in groupby(endpoint_name_raw):
#            endpoint_dict[key] = len(list(group))
#        # Ordering according to SQL query return
#        endpoint_dict = collections.OrderedDict(sorted(endpoint_dict.items(),key=lambda pair:pair[0].lower()))
#
#        # Parsing result
#        val_dict = {'timestamp':None,self.payload_field:None}
#        val_raw_dict = {}
#        val_cal_list = []
#        index = 0
#        logger.debug('Database log query return for endpoints {}'.format(endpoint_dict.keys()))
#        for endpoint,times in endpoint_dict.items():
#            val_raw_dict[endpoint] = []
#            ept_timestamp_list = []
#            for i in range(times):
#                val_raw_dict[endpoint].append(val_dict.copy())
#                query_row = query_return[index]
#                val_raw_dict[endpoint][i]['timestamp'] = query_row['timestamp'].strftime(constants.TIME_FORMAT)
#                val_raw_dict[endpoint][i][self.payload_field] = query_row[self.payload_field]
#                ept_timestamp_list.append('{} {{{}}}'.format(val_raw_dict[endpoint][i][self.payload_field],val_raw_dict[endpoint][i]['timestamp']))
#                index += 1
#            ept_timestamp_results = ', '.join(ept_timestamp_list)
#            val_cal_list.append('{} -> {}'.format(endpoint,ept_timestamp_results))
#
#        return {'value_raw': val_raw_dict, 'value_cal': '\n'.join(val_cal_list)}
#
#
#    def get_single_log(self, start_timestamp, end_timestamp, *args):
#        '''
#        Method to retrieve all database values for subset of endpoints between two timestamps.
#        Both input timestamps must be follow the format of constants.TIME_FORMAT, i.e. YYYY-MM-DDThh:mm:ssZ
#        start_timestamp (str): oldest timestamp for query into database
#        ending_timesamp (str): most recent timestamp for query into database
#        *args: list of endpoints of interest
#        '''
#        start_timestamp = str(start_timestamp)
#        end_timestamp = str(end_timestamp)
#        if len(args) == 0:
#            raise DriplineValueError('requires at least one endpoint arg provided')
#
#        # Parsing timestamps
#        self._try_parsing_date(start_timestamp)
#        self._try_parsing_date(end_timestamp)
#        if not end_timestamp > start_timestamp:
#            raise DriplineValueError('end_timestamp ("{}") must be > start_timestamp ("{}")!'.format(end_timestamp,start_timestamp))
#
#        # Connect to id map table + assign alises
#        self._connect_id_table()
#        t = self.table.alias()
#
#        outdict = {}
#        for endpoint in args:
#            ept_id = self._get_endpoint_id(endpoint)
#            # Select query + result
#            logger.debug('querying database for endpoint "{}" entries between "{}" and "{}"'.format(endpoint,start_timestamp,end_timestamp))
#            s = sqlalchemy.select([t]).where(sqlalchemy.and_(t.c.endpoint_id==ept_id,t.c.timestamp>start_timestamp,t.c.timestamp<end_timestamp)).order_by(t.c.timestamp.asc())
#            query_return = self.provider.engine.execute(s).fetchall()
#            if not query_return:
#                logger.warning('no entries found between "{}" and "{}"'.format(start_timestamp,end_timestamp))
#
#            outdict[endpoint] = [[entry['timestamp'].strftime(constants.TIME_FORMAT),entry['value_cal'],entry['value_raw']]for entry in query_return]
#
#        fp = open(os.path.expanduser('~')+'/sqldump.txt','w')
#        json.dump(obj=outdict,fp=fp)
#        fp.close()
#
#        return {'value_raw': True, 'value_cal': "Files written to ~/sqldump.txt"}
#
#
#    def get_latest(self, timestamp, endpoint_list):
#        '''
#        Method to retrieve last database value for all endpoints in list.  Used as part of standard DAQ operation
#        timestamp (str): timestamp upper bound for selection. Format must follow constants.TIME_FORMAT, i.e. YYYY-MM-DDThh:mm:ssZ
#        endpoint_list (list): list of endpoint names (str) of interest. Usage for dragonfly CLI e.g. endpoint_list='["endpoint_name1","endpoint_name_2",...]'
#        '''
#        timestamp = str(timestamp)
#        if isinstance(endpoint_list, list):
#            endpoint_list = [str(item) for item in endpoint_list]
#        else:
#            logger.error('Received type "{}" for argument endpoint_list instead of Python list'.format(type(endpoint_list).__name__))
#            raise DriplineValueError('expecting a list but received type {}'.format(type(endpoint_list).__name__))
#
#        # Parsing timestamp
#        self._try_parsing_date(timestamp)
#
#        # Connect to id map table + assign alises
#        self._connect_id_table()
#        t = self.table.alias()
#
#        # Select query + result
#        val_cal_list = []
#        val_raw_dict = {}
#
#        for name in endpoint_list:
#
#            ept_id = self._get_endpoint_id(name)
#
#            s = sqlalchemy.select([t]).where(sqlalchemy.and_(t.c.endpoint_id == ept_id,t.c.timestamp < timestamp))
#            s = s.order_by(t.c.timestamp.desc()).limit(1)
#            try:
#                query_return = self.provider.engine.execute(s).fetchall()
#            except DriplineDatabaseError as dripline_error:
#                logger.error('{}; in executing SQLAlchemy select statement for endpoint "{}"'.format(dripline_error.message,name))
#                return
#            if not query_return:
#                logger.critical('no records found before "{}" for endpoint "{}" in database hence not recording its snapshot'.format(timestamp,name))
#                continue
#            else:
#                val_raw_dict[name] = [{'timestamp' : query_return[0]['timestamp'].strftime(constants.TIME_FORMAT),
#                                       self.payload_field : query_return[0][self.payload_field]}]
#                val_cal_list.append('{} -> {} {{{}}}'.format(name,val_raw_dict[name][0][self.payload_field],val_raw_dict[name][0]['timestamp']))
#
#        return {'value_raw': val_raw_dict, 'value_cal': '\n'.join(val_cal_list)}
#
#
#    def _try_parsing_date(self, timestamp):
#        '''
#        Checks if timestamp (str) is in correct format for database query
#        '''
#        try:
#            return datetime.strptime(timestamp, constants.TIME_FORMAT)
#        except ValueError:
#            raise DriplineValueError('"{}" is not a valid timestamp format, use "YYYY-MM-DDThh:mm:ss.usZ"'.format(timestamp))
#
#
#    def _connect_id_table(self):
#        '''
#        Connects to the 'endpoint_id_map' table in database
#        '''
#        try:
#            self.it = sqlalchemy.Table('endpoint_id_map',self.provider.meta, autoload=True, schema=self.schema)
#        except DriplineDatabaseError as dripline_error:
#            logger.error('{}; when establishing connection to the "endpoint_id_map" table'.format(dripline_error.message))
#
#    def _get_endpoint_id(self, endpoint):
#        '''
#        Queries database to match endpoint to endpoint id
#        '''
#        id_table = self.it.alias()
#        s = sqlalchemy.select([id_table.c.endpoint_id]).where(id_table.c.endpoint_name == endpoint)
#        query_return = self.provider.engine.execute(s).fetchall()
#        if not query_return:
#            raise DriplineDatabaseError("Endpoint with name '{}' not found in database".format(endpoint))
#        ept_id = query_return[0]['endpoint_id']
#        logger.debug("Endpoint id '{}' matched to endpoint '{}'".format(ept_id, endpoint))
#        return ept_id
