# dripline-python
Python implementation of the Dripline framework

The python documentation is done via sphinx and is hosted on readthedocs.
You can find [it here](http://www.project8.org/dripline).

# Quick-start
The installation of dripline-python is done via setuptools and so the standard pip-based procedures should work.
More detailed notes are on the [getting started page](https://dripline-python.readthedocs.io/en/master/getting_started.html), along with description of the dependencies.

# Repo navigation
The repo is organized with the following subdirectories
- `doc`: contains the reStructuredText files used to build sphinx documentation (along with supporting files)
- `module_bindings`: contains C++ code to bind dripline-cpp (a git submodule) and to build the `_dripline` python package
- `dripline`: is the top of the pure-python package source tree
- `bin`: directory of python-implemented CLI utlities
- `examples`: contains example configuration files compatible with the dl-serve command.
              some will require details be filled in before they work
