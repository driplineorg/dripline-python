__all__ = []

import dripline

import importlib.util
import inspect

import logging
logger = logging.getLogger('dripline')


__all__.append('ObjectCreator')
class ObjectCreator:
    '''
    '''

    def __init__(self, **kwargs):
        '''
        '''
        pass

    def create_object(self, config, default_module: str, auth = None):
        logger.debug(f"Creating object from:\n\n{config}")

        module_name = config.pop('module', default_module)
        module_path = config.pop('module_path', False)
        extra_namespace = object()
        if module_path:
            try:
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
        #second priority, if it is in any extensions installed
        elif hasattr(dripline.extensions, module_name):
            module = getattr(dripline.extensions, module_name)
        ## Note: we only loop one layer down in the config file, this could possibly be made more generic
        else:
            for m in [getattr(dripline.extensions, i_mod) for i_mod in dir(dripline.extensions)]:
                if inspect.ismodule(m):
                    if hasattr(m, module_name):
                        module = getattr(m, module_name)

        if module is None: # continue above elifs
        #third priority, if it is part of the base set of implementations
            if hasattr(dripline.implementations, module_name):
                module = getattr(dripline.implementations, module_name)
        #fourth priority, if it is in core
            elif hasattr(dripline.core, module_name):
                module = getattr(dripline.core, module_name)
            else:
                raise NameError('no module "{}" in available namespaces'.format(module_name))
            
        if auth is not None:
            logger.debug("creating object with authentication")
            the_object = module( authentication_obj=auth, **config )
        else:
            the_object = module( **config )

        return the_object
