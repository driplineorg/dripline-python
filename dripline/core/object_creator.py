__all__ = []

import dripline

import importlib.util
import inspect

import logging
logger = logging.getLogger('dripline')


__all__.append('ObjectCreator')
class ObjectCreator:
    '''
    Mixin class providing the ability to create a class based on a provided configuration dictionary.
    '''

    def __init__(self, **kwargs):
        '''
        '''
        pass

    def create_object(self, config: dict, default_module: str, auth = None):
        '''
        Creates the object.

        Parameters
        ----------
            config: dict
                Configuration details.  Should contain the 'module' (optional; default will be used otherwise) and 'module_path' (optional, if not part of the Python path).
            default_module: str
                Module name used by default if `config` does not contain the key 'module'.
            auth: scarab.authentication, optional
                Optional authentication object that, if present, will be passed to the object's `__init__()` function as `authentication_obj`.

        '''
        logger.debug(f"Creating object from:\n\n{config}")

        module_name = config.pop('module', default_module)
        module_path = config.pop('module_path', False)
        extra_namespace = object()
        if module_path:
            try:
                logger.debug(f'Loading module path: {module_path}')
                spec = importlib.util.spec_from_file_location('extra_namespace', module_path)
                extra_namespace = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(extra_namespace)
            except IOError as e:
                logger.error("unable to load source from: {}".format(module_path))
                raise e

        module = None
        #first priority, if it is in the module_path provided (if any)
        if hasattr(extra_namespace, module_name):
            module = getattr(extra_namespace, module_name)
            logger.debug(f'Found module {module_name} in provided path')
        #second priority, if it is in any extensions installed
        elif hasattr(dripline.extensions, module_name):
            module = getattr(dripline.extensions, module_name)
            logger.debug(f'Found module {module_name} in dripline.extensions')
        ## Note: we only loop one layer down in the config file, this could possibly be made more generic
        else:
            for m in [getattr(dripline.extensions, i_mod) for i_mod in dir(dripline.extensions)]:
                if inspect.ismodule(m):
                    if hasattr(m, module_name):
                        module = getattr(m, module_name)
                        logger.debug(f'Found module {module_name} in dripline.extensions.{m.__name__}')

        if module is None: # continue above elifs
        #third priority, if it is part of the base set of implementations
            if hasattr(dripline.implementations, module_name):
                module = getattr(dripline.implementations, module_name)
                logger.debug(f'Found module {module_name} in dripline.implementations')
        #fourth priority, if it is in core
            elif hasattr(dripline.core, module_name):
                module = getattr(dripline.core, module_name)
                logger.debug(f'Found module {module_name} in dripline.core')
            else:
                raise NameError('no module "{}" in available namespaces'.format(module_name))
            
        if auth is not None:
            logger.debug("creating object with authentication")
            the_object = module( authentication_obj=auth, **config )
        else:
            the_object = module( **config )
        logger.debug(f'Object type: {type(the_object)}')

        return the_object
