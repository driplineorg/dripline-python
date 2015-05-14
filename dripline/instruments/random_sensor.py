from __future__ import absolute_import

from random import random

from ..core import Endpoint

__all__ = ['random_sensor']

class random_sensor(Endpoint):
    def __init__(self, name):
        self.name = name

    def on_get(self):
        return str(random())

    def on_set(self):
        raise NotImplementedError
