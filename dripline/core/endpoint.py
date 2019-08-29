__all__ = []

import scarab
from _dripline.core import _Endpoint
#import ipdb

__all__.append('Endpoint')
class Endpoint(_Endpoint):
    def __init__( self, name ):
        _Endpoint.__init__( self, name )
        self.int_attribute = 3
        self.float_attribute = 6.87
        self.bool_attribute = False
        self.str_attribute = "Hi"

    def do_get_request( self, a_request_message ):
        a_specifier =  a_request_message.specifier.to_string()
        if ( a_specifier ):
            try:
                an_attribute = getattr( self, a_specifier )
                the_node = scarab.ParamNode()
                the_node["values"] = scarab.ParamArray()
                the_node["values"].push_back(scarab.ParamValue(an_attribute))
                return a_request_message.reply(payload=the_node)
            except AttributeError:
                #TODO we should resolve the returncodes and update this value
                return a_request_message.reply( 201, "attribute error: {}".format(this_error.message) )
        else:
            try:
                the_value = self.on_get()
                payload = scarab.ParamNode()
                payload["values"] = scarab.ParamValue(the_value)
                return a_request_message.reply(payload=payload)
            #TODO should work out exception details and make the following block more narrow
            except Exception as e:
                return a_request_message.reply( 100, "got an exception trying to on_get: {}".format(str(e)))

    def do_set_request( self, a_request_message ):
        a_specifier =  a_request_message.specifier.to_string()
        new_value = a_request_message.payload["values"][0]()
        new_value = getattr(new_value, "as_"+new_value.type())
        print('new_value is [{}]'.format(new_value))
        if ( a_specifier ):
            try:
                setattr( self, a_specifier, a_payload_value)
                return a_request_message.reply()
            except AttributeError as this_error:
                return a_request_message.reply(201, "attribute error: {}".format(this_error.message) )
        else:
            try:
                result = self.on_set(new_value)
                return a_request_message.reply(payload=result)
            except Exception as e:
                return a_request_message.reply(100, "got an exception trying to on_get: {}".format(str(e)))

    def do_cmd_request( self, a_request_message ):
        #Note: any command executed in this way must return a Param object, otherwise the return will fail
        #TODO: We need to implement a helper for converting a semi-arbitrary (compatible) python data structure to a Param
        #      that way we can use this to call any method, methods can just return whatever is natural and the packaging be done here
        method_name = a_request_message.parsed_specifier().to_string()
        try:
            method_ref = getattr(self, method_name)
        except AttributeError as e:
            return a_request_message.reply(100, "error getting command's corresponding method: {}".format(str(e)))
        #TODO: this if/else block duplciates `get_value`, but it has no overload for returning a ParamNode (since it isn't a ParamValue)
        #      should there be a "get" (or get_item?) which is similar but returns any Param at the index, still allowing a default?
        if "values" in a_request_message:
            the_args = a_request_message.payload["values"]
        else:
            the_args = []
        #TODO: need to bind iterators for ParamNode so that we can populate unknown kwargs...
        #      python's dict has a keys(), that would let me force the above, or I could implement that in python from an iterator
        the_kwargs = {}
        try:
            result = method_ref(*the_args, **the_kwargs)
            return a_request_message.reply(payload=result)
        except Exception as e:
                #TODO: should be using a logger object here, right?
                print("failure while trying to execute: {}(*{}, **{})".format(method_name, str(the_args), str(the_kwargs)))
                return a_request_message.reply(100, "got an exception trying to execute cmd: {}".format(str(e)))

    def on_get( self ):
        '''
        placeholder method for getting the value of an endpoint.
        Implementations may override to enable OP_GET operations.
        The implementation must return a value which is able to be passed to the ParamValue constructor.
        '''
        #TODO should this be a dripline error?
        raise NotImplementedError( "endpoint '{}' does not implement an on_get".format(self.name) )

    def on_set( self ):
        '''
        placeholder method for setting the value of an endpoint.
        Implementations may override to enable OP_SET operations.
        Any returned object must already be a scarab::Param object
        '''
        #TODO should this be a dripline error?
        raise NotImplementedError( "endpoint '{}' does not implement an on_set".format(self.name) )
