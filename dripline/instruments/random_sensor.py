from __future__ import absolute_import

from random import random

from ..core import AutoReply

__all__ = ['random_sensor']

class random_sensor(AutoReply):
    def __init__(self, name):
        self.name = name

    def on_get(self):
        return str(random())

    def on_set(self):
        raise NotImplementedError
