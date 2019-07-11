import dripline
class Endpoint(dripline.core._Endpoint):
    def __init__( self, _name ):
        self.name = _name
        
    def do_get_request( self, a_request_message ):
        if ( a_request_message.parced_specifier != "" ):
            if ():
                return dripline.core._Endpoint.do_get_request( _message )
        else:
            raise dripline.NotImplemented
        
    def do_set( self, _value ):
        self.value = _value
