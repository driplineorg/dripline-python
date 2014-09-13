'''
This is an awful hack and we should move away from it and use inspect instead.
'''

from ..instruments import kv_store

__all__ = ['reg', 'constructor_registry']

constructor_registry = {
    'kv_store': kv_store.KVStore,
    'kv_store_key': kv_store.KVStoreKey
}

class reg(dict):
    def __init__(self):
        self.update(constructor_registry)
