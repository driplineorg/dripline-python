from .calibrate import calibrate
from .endpoint import Endpoint
__all__ = []

__all__.append("KeyValueStore")
class KeyValueStore(Endpoint):

    def __init__(self, initial_value=None, **kwargs):
        Endpoint.__init__(self, **kwargs)
        self._value = initial_value

    @calibrate()
    def on_get(self):
        print("in K.V.S. on_get")
        return self._value

    def on_set(self, new_value):
        print("in K.V.S. on_set")
        self._value = new_value
