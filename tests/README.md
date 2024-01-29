* Testing dripline-python

The dripline-python unit tests are setup to be used with the [pytest](https://pytest.org) framework.

** Running tests

All tests in the `tests` directory can be run by invoking the `pytest` command:

dl-py/tests> pytest

This will run all files in the current directory and its subdirectories matching the patterns `test_*.py` and `*_test.py`.
By convention, `test_*.py` is used for dl-python test files.
