===============
Getting Started
===============


System Requirements
*******************

Dripline-python is developed specifically for container-based workflows, including development and deployment, 
and that is the only approach we encourage or fully support.

Dripline-python has also been used directly on host systems including MacOS and Debian/Ubuntu Linux.  
It has not been tested on Windows systems.

We have not attempted to fully track compatible versions of all dependencies, or minimal versions.
We do, however, know the following:

* Dripline-python requires Python >= 3.6 because it leverages the f-string feature
* When not explicitly pinned in the setup.py file or Dockerfile, the "current" versions are installed from PyPI when developing and testing
* Tagged container images are believed to work, you should be able to run any of them and use ``pip freeze`` to check the full set of versions from the time of any available tag.

If you are using Dripline in a Docker container, please go directly to :ref:`docker_containers`.

Non-Python Dependencies
*************************

Dripline-python is wraps and extends the C++ package `dripline-cpp <https://dripline-cpp.readthedocs.io/en/latest/>`_. 
To install dripline-cpp, please consult its 
`installation instructions <https://dripline-cpp.readthedocs.io/en/latest/building.html>`_ (use the "standalone" option).  
We recommend you set the CMake variable ``PBUILDER_PY_INSTALL_IN_SITELIB`` to ``TRUE`` so that the scarab 
python package is installed in the Python site-packages directory.  
If you install dripline-cpp in a non-system installation location (e.g. with the default install prefix, 
which is inside the build directory), you will need to know the location of the installed CMake config files 
for the dripline-python build below (usually ``[prefix]/lib/cmake/Dripline``).  As an alternative, you could 
make a system-wide install at ``/usr/local``.

Dripline-cpp currently requires (all versions are minima): C++17 (via gcc or clang), CMake v3.5, 
Boost 1.46, rapidjson 1.0, yaml-cpp, and rabbitmq-c.  
Everything should be available from standard package managers.

The Python wrapping of C++ code is done with `Pybind11 <https://pybind11.readthedocs.io/>`_.  
Version 2.6.0 or higher is required.  
It can be installed from most package managers or by following their instructions. 

You will need `CMake <https://cmake.org/>`_ to build the C++ wrappers.  
Version 3.5 or higher is required.  
It can be installed from most package managers or by following their instructions.
Note that this is not included as a dependency in the Python installation process.  
See ``pyproject.toml`` for more details.

Python Libraries
****************

If working with containers, the dependencies should all be installed (generally from PyPI).  
If installing on a host machine, you will need to be careful about the potential for 
conflicting dependency versions (which, ideally, should be done in a virtual environment).  

Required
--------

The following dependencies are required for core functionality and thus non-optional.

`PyYAML <http://pyyaml.org>`_ is used to read yaml formatted configuration files.

`asteval <https://newville.github.io/asteval/>`_ is used to process python statements presented as strings 
(sometimes provided as strings in start-up configurations or as part of calibration definitions).


Building Docs [doc]
~~~~~~~~~~~~~~~~~~~

`Sphinx <http://sphinx-doc.org/>`_ is required to compile this documentation.

.. `Sphinx-contrib-programoutput <http://pythonhosted.org/sphinxcontrib-programoutput/>`_ Is used to automatically include the --help for the various utility programs.

.. removing better-apidoc use, we should confirm we want/need to use this, or look into normal apidoc
   `better-apidoc <https://pypi.python.org/pypi/better-apidoc>`_ is used to automatically generate rst files with api documentation.


Color Output
~~~~~~~~~~~~
`Colorlog <http://pypi.python.org/pypi/colorlog>`_ is completely aesthetic.
The logging module is used throughout dripline and this allows for colorized format of log messages.


Helpful Python Packages
~~~~~~~~~~~~~~~~~~~~~~~
The following packages are not actually dependencies for any aspect of dripline.
They are, however, highly recommended (especially for anyone relatively new to python).

`ipython <http://ipython.org>`_ and `ipdb <http://www.pypi.python.org/pypi/ipdb>`_ are both highly recomended 
for all non-production workflows.
The expanded tab completion, command and output history, and doc access make it a powerful python interpretor 
for developing or manually interacting with dripline components.



Installation
************

We highly recommend using dripline-python in a Docker container.  However, there is nothing to prevent 
installing and running directly on your host system.  For using Docker containers, see the next section.  
For installing on a host machine, skip to :ref:`host_install`.


.. _docker_containers:

Docker containers
-----------------

If you're new to containers, consider starting with the 
`getting started docs from Docker Inc. <https://www.docker.com/get-started>`_; 
most contributors develop using the OS-native "desktop application" available there.

The easiest way to get started with dripline is simply to use a container image from the 
`dockerhub repository <https://hub.docker.com/r/driplineorg/dripline-python/>`_.
These are built automatically based on tagged releases, as well as merges into the main or develop branch.
Images are automatically built for both x86 and armv7 architectures, and a container manifest allows 
use of common tag references to resolve to the architectures-specific images.

You may also use the ``Dockerfile`` located in the dripline-python GitHub repository's root directory 
to build the image yourself (the full repository is the required build context).
Note that the Dockerfile provides arguments for specifing the base image details, the defaults there will 
hopefully be kept current, but the automatic build configurations actively pass overrides based on 
the GitHub Actions ``publish.yaml`` file (``.github/workflows/publish.yaml``).

.. _host_install:

Direct installation
-------------------

We highly recommend using a virtual environment for this installation (e.g. virtualenv or conda).

First, clone the dripline-python repository: 

  ``> git clone git@github.com:driplineorg/dripline-python``

or download a zip file of the source from `GitHub <https://github.com/driplineorg/dripline-python>`_ and unpack it.

From the top directory of dripline-python, build with ``pip``.  You have a few options for what that command looks like:

If dripline-cpp was installed in a system location (e.g. `/usr/local`), that will look like:

  ``> pip install .``

If you want to install so that you can edit the dripline-python code, use the ``-e`` option: 

  ``> pip install -e .``

If you need to specify the location of dripline-cpp, set the ``Dripline_DIR`` environment variable first, e.g.:

  ``> Dripline_DIR=/install/prefix/lib/cmake/Dripline pip install .``
