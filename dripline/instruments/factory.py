'''
This is an awful hack and we should move away from it and use inspect instead.
'''

import kv_store

constructor_registry = {
    'kv_store': kv_store.KVStore,
    'kv_store_key': kv_store.KVStoreKey
}
