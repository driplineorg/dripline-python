import dripline.core, scarab

def test_request_create_default():
    a_request = dripline.core.MsgRequest.create()
    assert(isinstance(a_request, dripline.core.MsgRequest))
    assert(a_request.is_request())
    assert(not a_request.is_reply())
    assert(not a_request.is_alert())
    assert(a_request.lockout_key_valid)
    assert(a_request.payload.is_null())
    assert(a_request.message_operation == dripline.core.op_t.unknown)
    assert(a_request.routing_key == "")
    assert(a_request.specifier.to_string() == "")
    assert(a_request.reply_to == "")
    assert(a_request.encoding.name == "json")
    assert(len(a_request.correlation_id) == 36)

def test_request_create_nondefault():
    a_payload = scarab.ParamNode()
    a_payload.add("p1", scarab.ParamValue(1))
    a_payload.add("p2", scarab.ParamValue(2))
    a_msg_op = dripline.core.op_t.get
    a_routing_key = "hey"
    a_specifier = "heyy.1"
    a_reply_to = "a_receiver"
    a_request = dripline.core.MsgRequest.create(a_payload, a_msg_op, a_routing_key, a_specifier, a_reply_to)
    assert(isinstance(a_request, dripline.core.MsgRequest))
    assert(a_request.is_request())
    assert(not a_request.is_reply())
    assert(not a_request.is_alert())
    assert(a_request.lockout_key_valid)
    assert(a_request.payload.is_node())
    assert(a_request.payload.count("p1") == 1)
    assert(a_request.message_operation == a_msg_op)
    assert(a_request.routing_key == a_routing_key)
    assert(a_request.specifier.to_string() == a_specifier)
    assert(a_request.reply_to == a_reply_to)
    assert(a_request.encoding.name == "json")
    assert(len(a_request.correlation_id) == 36)

def test_request_reply_default():
    a_request = dripline.core.MsgRequest.create(reply_to = "a_receiver")
    a_reply = a_request.reply()
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == 0)
    assert(a_reply.return_message == "")
    assert(a_reply.payload.is_null())
    assert(a_reply.routing_key == a_request.reply_to)
    assert(a_reply.correlation_id == a_request.correlation_id)

def test_request_reply_nondefault():
    a_return_code = 788
    a_return_message = "a return message."
    a_payload = scarab.ParamValue(99)
    a_request = dripline.core.MsgRequest.create(reply_to = "a_receiver")
    a_reply = a_request.reply(a_return_code, a_return_message, a_payload)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.return_code == a_return_code)
    assert(a_reply.return_message == a_return_message)
    assert(a_reply.payload.is_value())
    assert(a_reply.routing_key == a_request.reply_to)
    assert(a_reply.correlation_id == a_request.correlation_id)

def test_reply_create_default():
    a_reply = dripline.core.MsgReply.create()
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.is_reply())
    assert(not a_reply.is_request())
    assert(not a_reply.is_alert())
    assert(a_reply.return_code == 0)
    assert(a_reply.return_message == "")
    assert(a_reply.payload.is_null())
    assert(a_reply.routing_key == "")
    assert(a_reply.specifier.to_string() == "")
    assert(a_reply.encoding.name == "json")
    assert(a_reply.correlation_id == "")

def test_reply_create1_nondefault():
    a_retcode = 1005
    a_message = "a message!"
    a_payload = scarab.ParamValue(87)
    a_routing_key = "hey"
    a_specifier = "heyy.11"
    a_reply = dripline.core.MsgReply.create(a_retcode, a_message, a_payload, a_routing_key, a_specifier)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.is_reply())
    assert(not a_reply.is_request())
    assert(not a_reply.is_alert())
    assert(a_reply.return_code == a_retcode)
    assert(a_reply.return_message == a_message)
    assert(a_reply.payload.is_value())
    assert(a_reply.routing_key == a_routing_key)
    assert(a_reply.specifier.to_string() == a_specifier)
    assert(a_reply.encoding.name == "json")
    assert(a_reply.correlation_id == "")

def test_reply_create2_nondefault():
    a_retcode = 2005
    a_message = "another message!"
    a_payload = scarab.ParamValue(87)
    a_request = dripline.core.MsgRequest.create(reply_to = "a_receiver")
    a_reply = dripline.core.MsgReply.create(a_retcode, a_message,a_payload, a_request)
    assert(isinstance(a_reply, dripline.core.MsgReply))
    assert(a_reply.is_reply())
    assert(not a_reply.is_request())
    assert(not a_reply.is_alert())
    assert(a_reply.return_code == a_retcode)
    assert(a_reply.return_message == a_message)
    assert(a_reply.payload.is_value())
    assert(a_reply.routing_key == a_request.reply_to)
    assert(a_reply.specifier.to_string() == "")
    assert(a_reply.encoding.name == "json")
    assert(a_reply.correlation_id == a_request.correlation_id)

def test_alert_create_default():
    an_alert = dripline.core.MsgAlert.create()
    assert(isinstance(an_alert, dripline.core.MsgAlert))
    assert(an_alert.is_alert())
    assert(not an_alert.is_reply())
    assert(not an_alert.is_request())
    assert(an_alert.payload.is_null())
    assert(an_alert.routing_key == "")
    assert(an_alert.specifier.to_string() == "")
    assert(an_alert.encoding.name == "json")
    assert(len(an_alert.correlation_id) == 36)

def test_alert_create_nondefault():
    a_payload = scarab.ParamValue(3)
    a_routing_key = "hey"
    a_specifier = "heyy.1"
    an_alert = dripline.core.MsgAlert.create(a_payload, a_routing_key, a_specifier)
    assert(isinstance(an_alert, dripline.core.MsgAlert))
    assert(an_alert.is_alert())
    assert(not an_alert.is_reply())
    assert(not an_alert.is_request())
    assert(an_alert.payload.is_value())
    assert(an_alert.routing_key == a_routing_key)
    assert(an_alert.specifier.to_string() == a_specifier)
    assert(an_alert.encoding.name == "json")
    assert(len(an_alert.correlation_id) == 36)

def test_message_encode_full_message():
    a_payload = scarab.ParamValue(99)
    messages = []
    messages.append(dripline.core.MsgRequest.create(payload = a_payload))
    messages.append(dripline.core.MsgReply.create(payload = a_payload))
    messages.append(dripline.core.MsgAlert.create(payload = a_payload))
    for i in range(3):
        a_full_message = messages[i].encode_full_message()
        assert(type(a_full_message) == str)
        assert(len(a_full_message) > 0)
        assert(type(eval(a_full_message) == dict))

def test_message_derived_modify_message_param():
    a_node = scarab.ParamNode()
    a_request = dripline.core.MsgRequest.create()
    a_request.derived_modify_message_param(a_node)
    a_dir = a_node.to_python()
    assert(len(a_dir) == 2)
    assert(len(a_dir['lockout_key']) == 36)
    assert(a_dir['message_operation'] == 0xffffffff)
    a_reply = dripline.core.MsgReply.create()
    a_reply.derived_modify_message_param(a_node)
    a_dir = a_node.to_python()
    assert(len(a_dir) == 4)
    assert(a_dir['return_code'] == 0)
    assert(a_dir['return_message'] == "")
    an_alert = dripline.core.MsgAlert.create()
    an_alert.derived_modify_message_param(a_node)
    a_dir = a_node.to_python()
    assert(len(a_dir) == 4)
