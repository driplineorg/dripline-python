import scarab, dripline.core

import pytest

def test_service_creation():
    a_name = "a_service"
    a_service = dripline.core.Service(a_name)
    assert(a_service.name == a_name)

def test_submit_request_message():
    a_name = "a_service"
    a_service = dripline.core.Service(a_name)
    a_request = dripline.core.MsgRequest.create(scarab.ParamValue(5), dripline.core.op_t.get, "hey", "name", "a_receiver")
    a_reply = a_service.submit_request_message(a_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0)
    assert(a_reply.correlation_id == a_request.correlation_id)
    a_reply.payload.to_python()['values'] == [a_name]

def test_on_request_message():
    a_name = "a_service"
    a_service = dripline.core.Service(a_name)
    a_request = dripline.core.MsgRequest.create(scarab.ParamValue(5), dripline.core.op_t.get, "hey", "name", "a_receiver")
    a_reply = a_service.on_request_message(a_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0) # 0
    assert(a_reply.correlation_id == a_request.correlation_id)
    a_reply.payload.to_python()['values'] == [a_name]

def test_on_reply_message():
    a_service = dripline.core.Service("hello")
    a_reply = dripline.core.MsgReply.create()
    with pytest.raises(dripline.core.DriplineError) as excinfo:
        a_service.on_reply_message(a_reply)

def test_on_alert_message():
    a_service = dripline.core.Service("hello")
    an_alert = dripline.core.MsgAlert.create()
    with pytest.raises(dripline.core.DriplineError) as excinfo:
        a_service.on_alert_message(an_alert)

def test_do_get_request_no_specifier():
    a_service = dripline.core.Service("hello")
    a_get_request = dripline.core.MsgRequest.create()
    with pytest.raises(dripline.core.ThrowReply) as excinfo:
        a_reply = a_service.do_get_request(a_get_request)

def test_do_get_request_invalid_specifier():
    a_service = dripline.core.Service("a_service")
    a_get_request = dripline.core.MsgRequest.create(scarab.ParamValue(5), dripline.core.op_t.get, "hey", "namee", "a_receiver")
    with pytest.raises(dripline.core.ThrowReply) as excinfo:
        a_reply = a_service.do_get_request(a_get_request)

def test_do_get_request_valid_specifier():
    a_name = "a_service"
    a_service = dripline.core.Service(a_name)
    a_get_request = dripline.core.MsgRequest.create(scarab.ParamValue(5), dripline.core.op_t.get, "hey", "name", "a_receiver")
    a_reply = a_service.do_get_request(a_get_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0)
    assert(a_reply.correlation_id == a_get_request.correlation_id)
    a_reply.payload.to_python()['values'] == [a_name]

def test_do_set_request_no_specifier():
    print("start test")
    a_service = dripline.core.Service("hello")
    the_node = scarab.ParamNode()
    the_node.add("values", scarab.ParamArray())
    the_node["values"].push_back(scarab.ParamValue("a_better_service"))
    a_set_request = dripline.core.MsgRequest.create(the_node, dripline.core.op_t.set, "hey")
    with pytest.raises(dripline.core.ThrowReply) as excinfo:
        a_reply = a_service.do_set_request(a_set_request)

def test_do_set_request_invalid_specifier():
    a_service = dripline.core.Service("a_service")
    the_node = scarab.ParamNode()
    the_node.add("values", scarab.ParamArray())
    the_node["values"].push_back(scarab.ParamValue("a_better_service"))
    a_set_request = dripline.core.MsgRequest.create(the_node, dripline.core.op_t.set, "hey", "namee", "a_receiver")
    with pytest.raises(dripline.core.ThrowReply) as excinfo:
        a_reply = a_service.do_set_request(a_set_request)

def test_do_set_request_valid_specifier():
    value1 = "a_service"
    value2 = "a_better_service"
    ## the service base class doesn't have any settable members, create one:
    class ServiceWithMember(dripline.core.Service):
        a_value = value1
    a_service = ServiceWithMember("a_service")
    the_node = scarab.ParamNode()
    the_node.add("values", scarab.ParamArray())
    the_node["values"].push_back(scarab.ParamValue(value2))
    a_set_request = dripline.core.MsgRequest.create(the_node, dripline.core.op_t.set, "hey", "a_value", "a_receiver")
    a_reply = a_service.do_set_request(a_set_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0)
    assert(a_reply.correlation_id == a_set_request.correlation_id)
    print(a_service.name)
    assert(a_service.a_value == value2)

def test_do_cmd_request_invalid_specifier():
    a_service = dripline.core.Service("a_service")
    a_cmd_request = dripline.core.MsgRequest.create(scarab.Param(), dripline.core.op_t.cmd, "hey", "on_gett", "a_receiver")
    with pytest.raises(dripline.core.ThrowReply) as excinfo:
        a_reply = a_service.do_cmd_request(a_cmd_request)

def test_do_cmd_request_valid_specifier():
    class AnotherService(dripline.core.Service):
        def __init__(self, name):
            dripline.core.Service.__init__(self, name)
        def a_method(self, n1, n2):
            return n1 + n2
    a_service = AnotherService("a_service")
    the_node = scarab.ParamNode()
    the_node.add("values", scarab.ParamArray())
    n1, n2 = 10, 13
    the_node["values"].push_back(scarab.ParamValue(n1))
    the_node["values"].push_back(scarab.ParamValue(n2))
    a_cmd_request = dripline.core.MsgRequest.create(the_node, dripline.core.op_t.cmd, "hey", "a_method", "a_receiver")
    a_reply = a_service.do_cmd_request(a_cmd_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0)
    assert(a_reply.correlation_id == a_cmd_request.correlation_id)
    assert(a_reply.payload.to_python() == n1 + n2)

def test_send_request():
    a_service = dripline.core.Service("a_service")
    a_request = dripline.core.MsgRequest.create(scarab.Param(), dripline.core.op_t.get, "hey", "on_get", "a_receiver")
    a_sent_msg = a_service.send(a_request)
    assert not a_sent_msg.successful_send
    assert 'Reply code: 312 NO_ROUTE' in a_sent_msg.send_error_message
