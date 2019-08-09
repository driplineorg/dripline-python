import scarab
import dripline
import ipdb
class Endpoint(dripline.core._Endpoint):
    def __init__( self, name ):
        dripline.core._Endpoint.__init__( self, name )
        self.int_attribute = 3
        self.float_attribute = 6.87
        self.bool_attribute = False
        self.str_attribute = "Hi"
        
    def do_get_request( self, a_request_message ):
        a_specifier =  a_request_message.parsed_specifier().to_string()
        if ( a_specifier ):
            try:
                if ( getattr(self, a_specifier, "NotFound") != "NotFound"):
                    an_attribute = getattr( self, a_specifier )
                    the_value = scarab.ParamValue( an_attribute )
                    the_array = scarab.ParamArray()
                    the_array.resize( 1 )
                    the_array.assign( 0, the_value )
                    the_node = scarab.ParamNode()
                    the_node.add( "values", the_array )
                    return a_request_message.reply( 0, "Success", the_node )
                else:
                    return a_request_message.reply( 200,  200, "Attribute {} does not exist in endpoint <{}>".format(a_specifier, self.name) )
            except AttributeError:
                return a_request_message.reply( 201, "attribute error: {}".format(this_error.message) )
        else:
            return self.on_get( a_request_message )

    def on_get( self, a_request ):
        return a_request.reply( 203, "Endpoint <{}> of type {} does not support Get".format(self.name, type(self)) )

    def do_set_request( self, a_request_message ):
        a_specifier =  a_request_message.parsed_specifier().to_string()
        if ( a_specifier ):
            try:
                if ( getattr(self, a_specifier, "NotFound") != "NotFound"):
                    print( "Current value of {} is: {}".format(a_specifier, getattr(self, a_specifier, "NotFound")) )
                    #ipdb.set_trace()
                    if( isinstance(getattr(self, a_specifier, "NotFound"), bool) ):
                        print("bool test")
                        a_payload_value = a_request_message.payload()["values"][0]().as_bool()
                    elif( isinstance(getattr(self, a_specifier, "NotFound"), float) ):
                        print("float test")
                        a_payload_value = a_request_message.payload()["values"][0]().as_double()
                    elif( isinstance(getattr(self, a_specifier, "NotFound"), int) ):
                        print("int test")
                        a_payload_value = a_request_message.payload()["values"][0]().as_int()
                    #elif( isinstance(getattr(self, a_specifier, "NotFound"), str) ):
                    #    print("str test")
                    #    a_payload_value = a_request_message.payload()["values"][0]().as_string()
                        
                    print( "Request message payload: {}".format(a_request_message.payload()) )
                    print( "Payload value: {}".format(a_payload_value) )
                    setattr( self, a_specifier, a_payload_value)
                    return a_request_message.reply( 0, "Changed {} to: {}".format(a_specifier, getattr(self, a_specifier, "NotFound")) )
                else:
                    return a_request_message.reply( 200, "Attribute {} does not exist in endpoint <{}>".format(a_specifier, self.name) )
            except AttributeError as this_error:
                return a_request_message.reply( 201, "attribute error: {}".format(this_error.message) )
        else:
            return self.on_get( a_request_message )
