import scarab
import dripline
class Endpoint(dripline.core._Endpoint):
    def __init__( self, name ):
        dripline.core._Endpoint.__init__( self, name )
        self.test_attribute = 3
        
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
                    an_attribute = getattr( self, a_specifier )
                    print( type( a_request_message.payload() ) )
                    print( "Request message payload: {}".format(a_request_message.payload()) )
                    return a_request_message.reply( 201, "TESTING" )
                    #the_value = scarab.ParamValue( an_attribute )
                    #the_array = scarab.ParamArray()
                    #the_array.resize( 1 )
                    #the_array.assign( 0, the_value )
                    #the_node = scarab.ParamNode()
                    #the_node.add( "values", the_array )
                    #return a_request_message.reply( 0, "Success", the_node )
                else:
                    return a_request_message.reply( 200, "Dripline.NotImplemented temporary message" )
            except AttributeError as this_error:
                print( "attribute error: {}".format(this_error.message ) )
                return a_request_message.reply( 201, "Attribute '" + a_specifier + "' does not exist in endpoint <" + self.name + ">" )
        else:
            return self.on_get( a_request_message )

            
    def test_function( self ):
        return "Inside python function"
