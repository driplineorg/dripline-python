__all__ = []

import scarab
from _dripline.core import _Endpoint

__all__.append('Endpoint')
class Endpoint(_Endpoint):
    '''
    Base class for all objects which can be sent dripline requests.
    Every object described in a runtime configuration passed to `dl-serve` should derive from this class (either directly or indirectly).
    '''
    def __init__(self, name):
        '''
        name (str) : the name of the endpoint, specifies the binding key for request messages to which this object should reply
        '''
        _Endpoint.__init__(self, name)

    def do_get_request(self, a_request_message):
        print("in get_request")
        a_specifier =  a_request_message.specifier.to_string()
        if (a_specifier):
            print("has specifier")
            try:
                print("specifier is: {}".format(a_specifier))
                an_attribute = getattr(self, a_specifier)
                print(an_attribute)
                print("attribute '{}' value is [{}]".format(a_specifier, an_attribute))
                the_node = scarab.ParamNode()
                the_node["values"] = scarab.ParamArray()
                the_node["values"].push_back(scarab.ParamValue(an_attribute))
                return a_request_message.reply(payload=the_node)
            except AttributeError as this_error:
                #TODO we should resolve the returncodes and update this value
                return a_request_message.reply(201, "attribute error: {}".format(this_error))
        else:
            print('no specifier')
            the_value = self.on_get()
            return a_request_message.reply(payload=scarab.to_param(the_value))

    def do_set_request(self, a_request_message):
        a_specifier =  a_request_message.specifier.to_string()
        new_value = a_request_message.payload["values"][0]()
        new_value = getattr(new_value, "as_"+new_value.type())()
        print('new_value is [{}]'.format(new_value))
        if ( a_specifier ):
            try:
                setattr(self, a_specifier, new_value)
                return a_request_message.reply()
            except AttributeError as this_error:
                return a_request_message.reply(201, "attribute error: {}".format(this_error))
        else:
            try:
                result = self.on_set(new_value)
                return a_request_message.reply(payload=scarab.to_param(result))
            except Exception as e:
                return a_request_message.reply(100, "got an exception trying to on_get: {}".format(str(e)))

    def do_cmd_request(self, a_request_message):
        # Note: any command executed in this way must return a python data structure which is
        #       able to be converted to a Param object (to be returned in the reply message)
        method_name = a_request_message.specifier.to_string()
        try:
            method_ref = getattr(self, method_name)
        except AttributeError as e:
            return a_request_message.reply(100, "error getting command's corresponding method: {}".format(str(e)))
        the_kwargs = a_request_message.payload.to_python()
        the_args = the_kwargs.pop('values', [])
        result = method_ref(*the_args, **the_kwargs)
        return a_request_message.reply(payload=scarab.to_param(result))

    def on_get(self):
        '''
        placeholder method for getting the value of an endpoint.
        Implementations may override to enable OP_GET operations.
        The implementation must return a value which is able to be passed to the ParamValue constructor.
        '''
        #TODO should this be a dripline error?
        raise NotImplementedError("endpoint '{}' does not implement an on_get".format(self.name))

    def on_set(self, _value):
        '''
        placeholder method for setting the value of an endpoint.
        Implementations may override to enable OP_SET operations.
        Any returned object must already be a scarab::Param object
        '''
        #TODO should this be a dripline error?
        raise NotImplementedError("endpoint '{}' does not implement an on_set".format(self.name))
