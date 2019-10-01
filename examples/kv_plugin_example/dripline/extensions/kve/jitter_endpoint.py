import random

from dripline.core.calibrate import calibrate
from dripline.core.entity import Entity
__all__ = []

__all__.append("JitterEndpoint")
class JitterEndpoint(Entity):

    def __init__(self, initial_value=None, jitter_fraction=0.1, **kwargs):
        Entity.__init__(self, **kwargs)
        self._value = initial_value
        self._jitter_fraction = jitter_fraction

    @calibrate()
    def on_get(self):
        return self._value * (self._jitter_fraction * random.random())

    def on_set(self, new_value):
        self._value = new_value
