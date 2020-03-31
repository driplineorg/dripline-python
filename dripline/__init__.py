from . import core
from . import implementations
from . import extensions

import logging
logger = logging.getLogger(__name__)

def __get_version():
    import scarab
    import pkg_resources
    #TODO: this all needs to be populated from setup.py and gita
    version = scarab.VersionSemantic()
    logger.info('version should be: {}'.format(pkg_resources.get_distribution('dripline').version))
    version.parse(pkg_resources.get_distribution('dripline').version)
    version.package = 'driplineorg/dripline-python'
    version.commit = 'na'
    core.add_version('dripline-python', version)
    return version
version = __get_version()

def __update_plugins():
    import importlib
    import pkgutil
    import scarab
    import dripline.extensions
    plugins = {
        name: importlib.import_module(name) for finder, name, ispkg in pkgutil.iter_modules(dripline.extensions.__path__, dripline.extensions.__name__+'.')
    }
    for finder, name, ispkg in pkgutil.iter_modules(dripline.extensions.__path__, dripline.extensions.__name__+'.'):
        logger.info("adding: '{}'".format(name))
        this_module = importlib.import_module(name)
        setattr( dripline.extensions, name.split('dripline.extensions.')[1], this_module)
        if hasattr(this_module, 'version'):
            logger.debug("it has a version")
            dripline.core.add_version(name, this_module.version)
__update_plugins()
