from dripline.core import calibrate
from dripline.core import Entity
from dripline.core import ThrowReply
from dripline.core import get_return_codes_dict
from dripline.core import DL_WarningNoActionTaken
__all__ = []

__all__.append("KeyValueStore")
class KeyValueStore(Entity):

    def __init__(self, initial_value=None, **kwargs):
        Entity.__init__(self, **kwargs)
        self._value = initial_value

    @calibrate()
    def on_get(self):
        print("in K.V.S. on_get")
        return self._value

    def on_set(self, new_value):
        print("in K.V.S. on_set")
        self._value = new_value

    def throw_something(self):
        print("in throw_something")
        raise ThrowReply('device_error', "in throw_something method, rasing device_error")
