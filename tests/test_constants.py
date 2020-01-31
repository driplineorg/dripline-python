import dripline.core

OP_T_SET = 0
OP_T_GET = 1
OP_T_RUN = 8
OP_T_CMD = 9
OP_T_UKW = 0xffffffff

MSG_T_REPLY = 2
MSG_T_REQUEST = 3
MSG_T_ALERT = 4
MSG_UNKNOWN = 0xffffffff

def test_op_t_values():
    item = dripline.core.op_t
    assert(item.set.value == OP_T_SET)
    assert(item.get.value == OP_T_GET)
    assert(item.run.value == OP_T_RUN)
    assert(item.cmd.value == OP_T_CMD)
    assert(item.unknown.value == OP_T_UKW)
    
def test_op_t_to_unit():
    item = dripline.core.op_t
    assert(item.to_unit(item.set) == OP_T_SET)
    assert(item.to_unit(item.get) == OP_T_GET)
    assert(item.to_unit(item.run) == OP_T_RUN)
    assert(item.to_unit(item.cmd) == OP_T_CMD)
    assert(item.to_unit(item.unknown) == OP_T_UKW)

def test_op_t_to_string():
    item = dripline.core.op_t
    assert(item.to_string(item.set) == "set")
    assert(item.to_string(item.get) == "get")
    assert(item.to_string(item.run) == "run")
    assert(item.to_string(item.cmd) == "cmd")
    assert(item.to_string(item.unknown) == "unknown")
    flag = False
    try:
        item.to_string(dripline.core.msg_t.request)
    except Exception:
        flag = True
    assert(flag)

def test_op_t_uint_to_op_t():
    item = dripline.core.op_t
    assert(item.to_op_t(OP_T_SET) == item.set)
    assert(item.to_op_t(OP_T_GET) == item.get)
    assert(item.to_op_t(OP_T_RUN) == item.run)
    assert(item.to_op_t(OP_T_CMD) == item.cmd)
    assert(item.to_op_t(OP_T_UKW) == item.unknown)
    flag = False
    try:
        item.to_op_t(1000)
    except Exception:
        flag = True
    assert(flag)

def test_op_t_string_to_op_t():
    item = dripline.core.op_t
    assert(item.to_op_t("set") == item.set)
    assert(item.to_op_t("get") == item.get)
    assert(item.to_op_t("run") == item.run)
    assert(item.to_op_t("cmd") == item.cmd)
    assert(item.to_op_t("unknown") == item.unknown)
    flag = False
    try:
        item.to_op_t("hello")
    except Exception:
        flag = True
    assert(flag)

def test_msg_t_values():
    item = dripline.core.msg_t
    assert(item.reply.value == MSG_T_REPLY)
    assert(item.request.value == MSG_T_REQUEST)
    assert(item.alert.value == MSG_T_ALERT)
    assert(item.unknown.value == MSG_T_UNKNOWN)
    
def test_msg_t_to_unit():
    item = dripline.core.msg_t
    assert(item.to_unit(item.reply) == MSG_T_REPLY)
    assert(item.to_unit(item.request) == MSG_T_REQUEST)
    assert(item.to_unit(item.alert) == MSG_T_ALERT)
    assert(item.to_unit(item.unknown) == MSG_T_UNKNOWN)

def test_msg_t_to_string():
    item = dripline.core.msg_t
    assert(item.to_string(item.reply) == "reply")
    assert(item.to_string(item.request) == "request")
    assert(item.to_string(item.alert) == "alert")
    assert(item.to_string(item.unknown) == "unknown")
    flag = False
    try:
        item.to_string(dripline.core.op_t.set)
    except Exception:
        flag = True
    assert(flag)

def test_msg_t_uint_to_msg_t():
    item = dripline.core.msg_t
    assert(item.to_msg_t(MSG_T_REPLY) == item.reply)
    assert(item.to_msg_t(MSG_T_REQUEST) == item.request)
    assert(item.to_msg_t(MSG_T_ALERT) == item.alert)
    assert(item.to_msg_t(MSG_T_UNKNOWN) == item.unknown)
    flag = False
    try:
        item.to_msg_t(1000)
    except Exception:
        flag = True
    assert(flag)

def test_msg_t_string_to_msg_t():
    item = dripline.core.msg_t
    assert(item.to_msg_t("reply") == item.reply)
    assert(item.to_msg_t("request") == item.request)
    assert(item.to_msg_t("alert") == item.alert)
    assert(item.to_msg_t("unknown") == item.unknown)
    flag = False
    try:
        item.to_msg_t("hello")
    except Exception:
        flag = True
    assert(flag)
