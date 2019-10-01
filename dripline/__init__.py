from . import core
from . import implementations
from . import extensions

def __update_plugins():
    import importlib
    import pkgutil
    import scarab
    import dripline.extensions
    plugins = {
        name: importlib.import_module(name) for finder, name, ispkg in pkgutil.iter_modules(dripline.extensions.__path__, dripline.extensions.__name__+'.')
    }
    for finder, name, ispkg in pkgutil.iter_modules(dripline.extensions.__path__, dripline.extensions.__name__+'.'):
        print("adding: '{}'".format(name))
        this_module = importlib.import_module(name)
        setattr( dripline.extensions, name.split('dripline.extensions.')[1], this_module)
        if hasattr(this_module, 'version'):
            print("it has a version")
            scarab.add_version(name, this_module.version)
__update_plugins()
