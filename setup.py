from setuptools import setup
from glob import glob

import sys
from setuptools.command.test import test as TestCommand

verstr = "none"
try:
    #verstr = open("VERSION").read().strip().replace(' ', '.')
    import subprocess
    verstr = subprocess.check_output(['git','describe','--long']).strip()
except EnvironmentError:
    pass
except:
    raise RuntimeError("unable to find version")


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []

        # for some reason we have to do this to get it to function correctly.
        self.pytest_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, because outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name='dripline',
    version=verstr,
    packages=['dripline','dripline/core','dripline/instruments'],
    scripts=glob('bin/*'),
    install_requires=['pika>=0.9.8', 'PyYAML', 'msgpack-python'],
    extras_require={
        'doc': ['sphinx', 'sphinx_rtd_theme', 'sphinxcontrib-programoutput'],# sphinx-argparse
    },
    url='http://www.github.com/project8/dripline',
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
)
