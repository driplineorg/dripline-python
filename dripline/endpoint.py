import dripline
class Endpoint(dripline.core._Endpoint):
    def __init__( self, name ):
        dripline.core._Endpoint.__init__( self, name )
        
    def do_get_request( self, a_request_message ):
        print( "|||||||||||||||||||||||||||||||||||||||||||||||||||||" )
        if ( a_request_message.parsed_specifier().to_string() != "" ):
            try:
                if ( getattr(self, a_request_message.parced_specifier().to_string(), "NotFound") != "NotFound"):
                    return a_request_message.parsed_specifier()
                else:
                    raise dripline.NotImplemented
            except AttributeError:
                print("Specifier not found and 'default' argument not passed for getattr()")
        else:
            print("No specifier declared (empty string)")
                
    def do_set( self, _value ):
        self.value = _value
