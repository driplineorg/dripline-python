import scarab
import dripline
class Endpoint(dripline.core._Endpoint):
    def __init__( self, name ):
        dripline.core._Endpoint.__init__( self, name )
        
    def do_get_request( self, a_request_message ):
        print( "|||||||||||||||||||||||||||||||||||||||||||||||||||||" )
        specifier =  a_request_message.parsed_specifier().to_string()
        if ( specifier ):
            try:
                if ( getattr(self, specifier, "NotFound") != "NotFound"):
                    return a_request_message.reply( 1, "Successs", scarab.ParamNode(getattr(self, specifier)) )
                else:
                    raise dripline.NotImplemented
            except AttributeError:
                return a_request_message.reply( 201, "Attribute '" + specifier + "' does not exist in endpoint <" + self.name + ">" )
        else:
            return self.on_get( a_request_message )

    def on_get( self, a_request ):
        return a_request.reply( 200, "Endpoint <{}> of type {} does not support Get".format(self.name, type(self)) )

    def do_set( self, _value ):
        self.value = _value

    def test_function( self ):
        return "Inside python function"
