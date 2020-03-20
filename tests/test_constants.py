import scarab, _dripline.core
from dripline.core import ThrowReply, DriplineError

OP_T_SET = 0
OP_T_GET = 1
OP_T_RUN = 8
OP_T_CMD = 9
OP_T_UKW = 0xffffffff

MSG_T_REPLY = 2
MSG_T_REQUEST = 3
MSG_T_ALERT = 4
MSG_T_UNKNOWN = 0xffffffff

def test_op_t_to_uint():
    item = _dripline.core.op_t
    assert(item.to_uint(item.set) == OP_T_SET)
    assert(item.to_uint(item.get) == OP_T_GET)
    assert(item.to_uint(item.run) == OP_T_RUN)
    assert(item.to_uint(item.cmd) == OP_T_CMD)
    assert(item.to_uint(item.unknown) == OP_T_UKW)

def test_op_t_to_string():
    item = _dripline.core.op_t
    assert(item.to_string(item.set) == "set")
    assert(item.to_string(item.get) == "get")
    assert(item.to_string(item.run) == "run")
    assert(item.to_string(item.cmd) == "cmd")
    assert(item.to_string(item.unknown) == "unknown")
    flag = False
    try:
        item.to_string(_dripline.core.msg_t.request)
    except TypeError:
        flag = True
    assert(flag)

def test_op_t_uint_to_op_t():
    item = _dripline.core.op_t
    assert(item.to_op_t(OP_T_SET) == item.set)
    assert(item.to_op_t(OP_T_GET) == item.get)
    assert(item.to_op_t(OP_T_RUN) == item.run)
    assert(item.to_op_t(OP_T_CMD) == item.cmd)
    assert(item.to_op_t(OP_T_UKW) == item.unknown)

def test_op_t_string_to_op_t():
    item = _dripline.core.op_t
    assert(item.to_op_t("set") == item.set)
    assert(item.to_op_t("get") == item.get)
    assert(item.to_op_t("run") == item.run)
    assert(item.to_op_t("cmd") == item.cmd)
    assert(item.to_op_t("unknown") == item.unknown)
    flag = False
    try:
        item.to_op_t("hello")
    except DriplineError:
        flag = True
    assert(flag)

def test_msg_t_to_uint():
    item = _dripline.core.msg_t
    assert(item.to_uint(item.reply) == MSG_T_REPLY)
    assert(item.to_uint(item.request) == MSG_T_REQUEST)
    assert(item.to_uint(item.alert) == MSG_T_ALERT)
    assert(item.to_uint(item.unknown) == MSG_T_UNKNOWN)

def test_msg_t_to_string():
    item = _dripline.core.msg_t
    assert(item.to_string(item.reply) == "reply")
    assert(item.to_string(item.request) == "request")
    assert(item.to_string(item.alert) == "alert")
    assert(item.to_string(item.unknown) == "unknown")
    flag = False
    try:
        item.to_string(_dripline.core.op_t.set)
    except TypeError:
        flag = True
    assert(flag)

def test_msg_t_uint_to_msg_t():
    item = _dripline.core.msg_t
    assert(item.to_msg_t(MSG_T_REPLY) == item.reply)
    assert(item.to_msg_t(MSG_T_REQUEST) == item.request)
    assert(item.to_msg_t(MSG_T_ALERT) == item.alert)
    assert(item.to_msg_t(MSG_T_UNKNOWN) == item.unknown)

def test_msg_t_string_to_msg_t():
    item = _dripline.core.msg_t
    assert(item.to_msg_t("reply") == item.reply)
    assert(item.to_msg_t("request") == item.request)
    assert(item.to_msg_t("alert") == item.alert)
    assert(item.to_msg_t("unknown") == item.unknown)
    flag = False
    try:
        item.to_msg_t("hello")
    except DriplineError:
        flag = True
    assert(flag)
