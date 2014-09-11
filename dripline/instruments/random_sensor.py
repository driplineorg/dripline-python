from sensor import AutoReply
from random import random

class RandomSensor(AutoReply):
    def __init__(self, name):
        self.name = name

    def on_get(self):
        return str(random())

    def on_set(self):
        raise NotImplementedError
