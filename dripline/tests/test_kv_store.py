""" test_kv_store.py
Testing module for the KV store.
"""
# boilerplate needed to get paths right
import sys, os
LOCALPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, LOCALPATH + '/../')

import pytest
import kv_store
from factory import constructor_registry as cr

@pytest.fixture
def basic_kv_store():
    return kv_store.KVStore('abc')

def test_kv_store_name(basic_kv_store):
    """
    Test that basic construction of a KV
    store works.
    """
    assert basic_kv_store.name == 'abc'

def test_kv_store_key_adding(basic_kv_store):
    """
    Test that adding a key works.
    """
    test_ep = kv_store.KVStoreKey('foo')
    basic_kv_store.add_endpoint(test_ep)
    assert test_ep.provider == basic_kv_store

def test_kv_store_key_retrieval(basic_kv_store):
    """
    Test that once we add a key to a KV store, we can
    then retrieve that key object.
    """
    test_ep = kv_store.KVStoreKey('foo')
    basic_kv_store.add_endpoint(test_ep)
    assert basic_kv_store.endpoint('foo') == test_ep

def test_kv_store_key_value_set(basic_kv_store):
    """
    We should be able to set the value of a key.
    """
    test_ep = kv_store.KVStoreKey('foo')
    basic_kv_store.add_endpoint(test_ep)
    test_ep.on_set(0.3)

def test_kv_store_value_retrieval(basic_kv_store):
    """
    We should be able to get the value of a key, once we
    have set the value of a key.
    """
    test_ep = kv_store.KVStoreKey('foo')
    basic_kv_store.add_endpoint(test_ep)
    test_ep.on_set(0.3)
    assert test_ep.on_get() == 0.3

def test_constructor_reg_kv_store():
    """
    Make sure the KVStore constructor is in the registry.
    """
    assert cr['kv_store'] == kv_store.KVStore

def test_constructor_reg_kv_key():
    """
    Make sure the KVStoreKey constructor is in the registry.
    """
    assert cr['kv_store_key'] == kv_store.KVStoreKey

def test_kv_key_initial_value(basic_kv_store):
    """
    Test that the initial value keyword works when passed
    as a dict.
    """
    test_args = {'initial_value': 0.3}
    test_key = kv_store.KVStoreKey('key',**test_args)
    basic_kv_store.add_endpoint(test_key)
    assert test_key.on_get() == 0.3
