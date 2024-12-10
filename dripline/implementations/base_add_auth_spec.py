'''
Contains the base class for adding authentication specifications

Intended usage:
'''

import scarab

import logging

logger = logging.getLogger(__name__)

__all__ = []

__all__.append('BaseAddAuthSpec')
class BaseAddAuthSpec:
    '''
    This class should contain functions to add the authentication specifications for all 
    services and interfaces provided in dl-py's dripline.implementations.
    '''

    def __init__(self):
        '''
        '''
        pass

    def add_postgres_auth_spec(self, app):
        '''
        Adds the postgres authentication spec to a scarab::main_app object
        '''
        auth_spec = {
            'username': {
                'default': 'postgres',
                'env': 'POSTGRES_USER',    
            },
            'password': {
                'default': 'postgres',
                'env': 'POSTGRES_PASSWORD',
            },
        }
        app.add_default_auth_spec_group( 'postgres', scarab.to_param(auth_spec).as_node() )
        logging.debug('Added postgres auth spec')

