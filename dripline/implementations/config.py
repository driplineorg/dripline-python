'''
Convenience functions for handling implementation-related configuration processes
'''
 
import scarab

__all__ = []

__all__.append('add_postgres_auth_spec')
def add_postgres_auth_spec(app):
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
