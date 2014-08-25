# boilerplate needed to get paths right
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest
from agilent34461a import Agilent34461a
from factory import constructor_registry

def test_reg_factory():
	c = constructor_registry['agilent34461a']
	assert c == Agilent34461a