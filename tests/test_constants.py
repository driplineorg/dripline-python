import dripline
import pytest

def test_op_t_to_int():
    item = dripline.core.op_t
    assert(item.to_uint(item.set) == item.set.value)
    assert(item.to_uint(item.get) == item.get.value)
    assert(item.to_uint(item.cmd) == item.cmd.value)
    assert(item.to_uint(item.unknown) == item.unknown.value)

def test_op_t_to_string():
    item = dripline.core.op_t
    assert(item.to_string(item.set) == item.set.name)
    assert(item.to_string(item.get) == item.get.name)
    assert(item.to_string(item.cmd) == item.cmd.name)
    assert(item.to_string(item.unknown) == item.unknown.name)
    with pytest.raises(TypeError):
        item.to_string(dripline.core.msg_t.request)

def test_op_t_int_to_op_t():
    item = dripline.core.op_t
    assert(item.to_op_t(item.set.value) == item.set)
    assert(item.to_op_t(item.get.value) == item.get)
    assert(item.to_op_t(item.cmd.value) == item.cmd)
    assert(item.to_op_t(item.unknown.value) == item.unknown)

def test_op_t_string_to_op_t():
    item = dripline.core.op_t
    assert(item.to_op_t(item.set.name) == item.set)
    assert(item.to_op_t(item.get.name) == item.get)
    assert(item.to_op_t(item.cmd.name) == item.cmd)
    assert(item.to_op_t(item.unknown.name) == item.unknown)
    with pytest.raises(Exception): # TODO: check what kind of exception this raises
        item.to_op_t("hello")

def test_msg_t_to_int():
    item = dripline.core.msg_t
    assert(item.to_uint(item.reply) == item.reply.value)
    assert(item.to_uint(item.request) == item.request.value)
    assert(item.to_uint(item.alert) == item.alert.value)
    assert(item.to_uint(item.unknown) == item.unknown.value)

def test_msg_t_to_string():
    item = dripline.core.msg_t
    assert(item.to_string(item.reply) == item.reply.name)
    assert(item.to_string(item.request) == item.request.name)
    assert(item.to_string(item.alert) == item.alert.name)
    assert(item.to_string(item.unknown) == item.unknown.name)
    with pytest.raises(TypeError):
        item.to_string(dripline.core.op_t.set)

def test_msg_t_int_to_msg_t():
    item = dripline.core.msg_t
    assert(item.to_msg_t(item.reply.value) == item.reply)
    assert(item.to_msg_t(item.request.value) == item.request)
    assert(item.to_msg_t(item.alert.value) == item.alert)
    assert(item.to_msg_t(item.unknown.value) == item.unknown)

def test_msg_t_string_to_msg_t():
    item = dripline.core.msg_t
    assert(item.to_msg_t(item.reply.name) == item.reply)
    assert(item.to_msg_t(item.request.name) == item.request)
    assert(item.to_msg_t(item.alert.name) == item.alert)
    assert(item.to_msg_t(item.unknown.name) == item.unknown)
    with pytest.raises(Exception): # TODO: check what kind of exception this raises
        item.to_msg_t("hello")
