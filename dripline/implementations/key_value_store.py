from dripline.core import calibrate
from dripline.core import Entity
from dripline.core import ThrowReply
from dripline.core import get_return_codes_dict
from dripline.core import DL_WarningNoActionTaken
__all__ = []

import logging
logger=logging.getLogger(__name__)

__all__.append("KeyValueStore")
class KeyValueStore(Entity):

    def __init__(self, initial_value=None, **kwargs):
        Entity.__init__(self, **kwargs)
        self._value = initial_value

    @calibrate()
    def on_get(self):
        logger.info("in K.V.S. on_get")
        return self._value

    def on_set(self, new_value):
        logger.info("in K.V.S. on_set")
        self._value = new_value

    def throw_something(self):
        logger.warning("in throw_something")
        raise ThrowReply('resource_error', "in throw_something method, rasing resource_error")
