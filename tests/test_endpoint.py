import scarab, dripline.core

def test_endpoint_creation():
    a_name = "an_endpoint"
    an_endpoint = dripline.core.Endpoint(a_name)
    assert(an_endpoint.name == a_name)

def test_submit_request_message():
    a_name = "an_endpoint"
    an_endpoint = dripline.core.Endpoint(a_name)
    a_request = dripline.core.MsgRequest.create(scarab.ParamValue(5), dripline.core.op_t.get, "hey", "name", "a_receiver")
    a_reply = an_endpoint.submit_request_message(a_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0)
    assert(a_reply.correlation_id == a_request.correlation_id)
    a_reply.payload.to_python()['values'] == [a_name]

def test_on_request_message():
    a_name = "an_endpoint"
    an_endpoint = dripline.core.Endpoint(a_name)
    a_request = dripline.core.MsgRequest.create(scarab.ParamValue(5), dripline.core.op_t.get, "hey", "name", "a_receiver")
    a_reply = an_endpoint.on_request_message(a_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0)
    assert(a_reply.correlation_id == a_request.correlation_id)
    a_reply.payload.to_python()['values'] == [a_name]

def test_on_reply_message():
    an_endpoint = dripline.core.Endpoint("hello")
    a_reply = dripline.core.MsgReply.create()
    flag = False
    try:
        an_endpoint.on_reply_message(a_reply)
    except Exception: # seems like this is not throwing an actual DriplineError, just a generic Exception. dripline.core.DriplineError
        flag = True
    assert(flag)

def test_on_alert_message():
    an_endpoint = dripline.core.Endpoint("hello")
    an_alert = dripline.core.MsgAlert.create()
    flag = False
    try:
        an_endpoint.on_alert_message(an_alert)
    except Exception: # seems like this is not throwing an actual DriplineError, just a generic Exception. dripline.core.DriplineError
        flag =True
    assert(flag)

def test_do_get_request_no_specifier():
    an_endpoint = dripline.core.Endpoint("hello")
    a_get_request = dripline.core.MsgRequest.create()
    flag = False
    try:
        a_reply = an_endpoint.do_get_request(a_get_request)
    except dripline.core.ThrowReply:
        flag = True
    assert(flag)

def test_do_get_request_invalid_specifier():
    an_endpoint = dripline.core.Endpoint("an_endpoint")
    a_get_request = dripline.core.MsgRequest.create(scarab.ParamValue(5), dripline.core.op_t.get, "hey", "namee", "a_receiver")
    correct_error = False
    try:
        a_reply = an_endpoint.do_get_request(a_get_request)
    except dripline.core.ThrowReply as e:
        correct_error = True
    assert(correct_error)

def test_do_get_request_valid_specifier():
    a_name = "an_endpoint"
    an_endpoint = dripline.core.Endpoint(a_name)
    a_get_request = dripline.core.MsgRequest.create(scarab.ParamValue(5), dripline.core.op_t.get, "hey", "name", "a_receiver")
    a_reply = an_endpoint.do_get_request(a_get_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0)
    assert(a_reply.correlation_id == a_get_request.correlation_id)
    a_reply.payload.to_python()['values'] == [a_name]

def test_do_set_request_no_specifier():
    print("start test")
    an_endpoint = dripline.core.Endpoint("hello")
    the_node = scarab.ParamNode()
    the_node["values"] = scarab.ParamArray()
    the_node["values"].push_back(scarab.ParamValue("a_better_endpoint"))
    a_set_request = dripline.core.MsgRequest.create(the_node, dripline.core.op_t.set, "hey")
    correct_error = False
    try:
        a_reply = an_endpoint.do_set_request(a_set_request)
    except dripline.core.ThrowReply as e:
        correct_error = True
    assert(correct_error)

def test_do_set_request_invalid_specifier():
    an_endpoint = dripline.core.Endpoint("an_endpoint")
    the_node = scarab.ParamNode()
    the_node["values"] = scarab.ParamArray()
    the_node["values"].push_back(scarab.ParamValue("a_better_endpoint"))
    a_set_request = dripline.core.MsgRequest.create(the_node, dripline.core.op_t.set, "hey", "namee", "a_receiver")
    correct_error = False
    try:
        a_reply = an_endpoint.do_set_request(a_set_request)
    except dripline.core.ThrowReply as e:
        correct_error = True
        print('content of error:\n{}'.format(dir(e)))
    assert(correct_error)

def test_do_set_request_valid_specifier():
    value1 = "an_endpoint"
    value2 = "a_better_endpoint"
    ## the endpoint base class doesn't have any settable members, create one:
    class EndpointWithMember(dripline.core.Endpoint):
        a_value = value1
    an_endpoint = EndpointWithMember("an_endpoint")
    the_node = scarab.ParamNode()
    the_node["values"] = scarab.ParamArray()
    the_node["values"].push_back(scarab.ParamValue(value2))
    a_set_request = dripline.core.MsgRequest.create(the_node, dripline.core.op_t.set, "hey", "a_value", "a_receiver")
    a_reply = an_endpoint.do_set_request(a_set_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0)
    assert(a_reply.correlation_id == a_set_request.correlation_id)
    print(an_endpoint.name)
    assert(an_endpoint.a_value == value2)

def test_do_cmd_request_invalid_specifier():
    an_endpoint = dripline.core.Endpoint("an_endpoint")
    a_cmd_request = dripline.core.MsgRequest.create(scarab.Param(), dripline.core.op_t.cmd, "hey", "on_gett", "a_receiver")
    correct_error = False
    try:
        a_reply = an_endpoint.do_cmd_request(a_cmd_request)
    except dripline.core.ThrowReply as e:
        correct_error = True
    except Exception as e:
        print("got a [{}]".format(type(e)))
    assert(correct_error)

def test_do_cmd_request_valid_specifier():
    class AnotherEndpoint(dripline.core.Endpoint):
        def __init__(self, name):
            dripline.core.Endpoint.__init__(self, name)
        def a_method(self, n1, n2):
            return n1 + n2
    an_endpoint = AnotherEndpoint("an_endpoint")
    the_node = scarab.ParamNode()
    the_node["values"] = scarab.ParamArray()
    n1, n2 = 10, 13
    the_node["values"].push_back(scarab.ParamValue(n1))
    the_node["values"].push_back(scarab.ParamValue(n2))
    a_cmd_request = dripline.core.MsgRequest.create(the_node, dripline.core.op_t.cmd, "hey", "a_method", "a_receiver")
    a_reply = an_endpoint.do_cmd_request(a_cmd_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0)
    assert(a_reply.correlation_id == a_cmd_request.correlation_id)
    assert(a_reply.payload.to_python() == n1 + n2)
