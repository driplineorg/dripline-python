from . import core
from . import extensions

def __get_version():
    import scarab
    #TODO: this all needs to be populated from setup.py and gita
    version = scarab.VersionSemantic(0,0,1)
    version.package = 'driplineorg/dripline-python'
    version.commit = 'cba321'
    core.add_version('dripline-python', version)
    return version
version = __get_version()

def __update_plugins():
    import importlib
    import pkgutil
    import dripline.extensions
    plugins = {
        name: importlib.import_module(name) for finder, name, ispkg in pkgutil.iter_modules(dripline.extensions.__path__, dripline.extensions.__name__+'.')
    }
    for finder, name, ispkg in pkgutil.iter_modules(dripline.extensions.__path__, dripline.extensions.__name__+'.'):
        setattr( dripline.extensions, name.split('dripline.extensions.')[1], importlib.import_module(name))
__update_plugins()
