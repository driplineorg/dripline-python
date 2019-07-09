class Endpoint(_Endpoint):
    def __init__( self, _name ):
        self.name = _name
        
    def do_get( self ):
        return self.value
        
    def do_set( self, _value ):
        self.value = _value
