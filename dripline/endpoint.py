import dripline
class Endpoint(dripline.core._Endpoint):
    def __init__( self, _name ):
        self.name = _name
        
    def do_get( self, _message ):
        if ( _message.is_request() ):
            return dripline.core._Endpoint.do_get_request( _message )
        
    def do_set( self, _value ):
        self.value = _value
