from setuptools import setup
from glob import glob

verstr = "none"
try:
    verstr = open("VERSION").read().strip().replace(' ','.')
    open("dripline/__version.py", mode="w").write("'''This file generated automatically'''\n\n__version__ = '" + verstr + "'")
except EnvironmentError:
    pass
except:
    raise RuntimeError("unable to find version")

setup(
    name = 'dripline',
    version = verstr,
    packages = ['dripline'],
    install_requires = ['pika>=0.9.14'],
    url = 'http://www.github.com/project8/dripline'
)
