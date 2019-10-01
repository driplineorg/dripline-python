from . import core
from . import extensions

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
