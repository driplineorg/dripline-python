import scarab
import dripline
import ipdb
class Endpoint(dripline.core._Endpoint):
    def __init__( self, name ):
        dripline.core._Endpoint.__init__( self, name )
        self.int_attribute = 3
        self.float_attribute = 6.87
        
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
                    return a_request_message.reply( 200, "Dripline.NotImplemented temporary message" )
            except AttributeError:
                return a_request_message.reply( 201, "Attribute '" + a_specifier + "' does not exist in endpoint <" + self.name + ">" )
        else:
            return self.on_get( a_request_message )

    def on_get( self, a_request ):
        return a_request.reply( 202, "Endpoint <{}> of type {} does not support Get".format(self.name, type(self)) )

    def do_set_request( self, a_request_message ):
        a_specifier =  a_request_message.parsed_specifier().to_string()
        if ( a_specifier ):
            try:
                if ( getattr(self, a_specifier, "NotFound") != "NotFound"):
                        if( isinstance(getattr(self, a_specifier, "NotFound"), int) ):
                            a_payload_value = a_request_message.payload()["values"][0]().as_int()
                        elif( isinstance(getattr(self, a_specifier, "NotFound"), float) ):
                            a_payload_value = a_request_message.payload()["values"][0]().as_double()
                    print( "Request message payload: {}".format(a_request_message.payload()) )
                    print( "Payload value: {}".format(a_payload_value) )
                    #self.test_attribute = a_request_message.payload().at("values")
                    setattr( self, a_specifier, a_payload_value)
                    print( "Changed {} to: {}".format(a_specifier, getattr(self, a_specifier, "NotFound")) ) 
                    return a_request_message.reply( 201, "TESTING" )
                else:
                    return a_request_message.reply( 200, "Dripline.NotImplemented temporary message" )
            except AttributeError as this_error:
                print( "attribute error: {}".format(this_error.message) )
                return a_request_message.reply( 201, "Attribute '" + a_specifier + "' does not exist in endpoint <" + self.name + ">" )
        else:
            return self.on_get( a_request_message )

            
    def test_function( self ):
        return "Inside python function"
