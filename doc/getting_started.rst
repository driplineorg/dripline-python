===============
Getting Started
===============


System Requirements
*******************
The development of dripline is being done primarily on OS X (with packages installed via homebrew and python packages through pip) and debian linux (with any system-packages from apt and python pacakges through pip).
Much work is also done in :ref:`docker_containers` described below.

We have not attempted to fully track compatible versions of all dependencies, or minimal versions.
We do, however, know the following:

* dripline-python requires python >= 3.6 because it leverages the f-string feature
* when not explicitly pinned in the setup.py file or Dockerfil, the "current" versions are installed from PyPI when developing and testing
* tagged container images are believed to work, you should be able to run any of them and use ``pip freeze`` to check the full set of versions from the time of any available tag.


Installation
************

Dripline-python is developed specifically for container-based workflows, including development and deployment, and that is the only approach we encourage or support.
In principle, there is nothing to prevent installing and running directly on your host system, but you will need to be careful about the potential for conflicting dependency versions (that should probably be done in a virtualenvironment, but that's up to you).
If you're new to containers, consider starting with the `getting started docs from Docker Inc. <https://www.docker.com/get-started>`_; most contributors develop using the OS-native "desktop application" available there.

.. _docker_containers:

Docker containers
-----------------

The easiest way to get started with dripline is simply to use a container image from the `dockerhub repository <https://hub.docker.com/r/driplineorg/dripline-python/>`_.
These are built automatically based on tagged releases, as well as merges into the master or develop branch.
Images are automatically built for both x86 and armv7 architectures, and a container manifest allows use of common tag references to resolve to the architectures-specific images.

You may also use the ``Dockerfile`` located in the dripline-python GitHub repository's root directory to build the image yourself (the full repository is the required build context).
Note that the Dockerfile provides arguments for specifing the base image details, the defaults there will hopefully be kept current, but the automatic build configurations actively pass overrides based on the ``.travis.yml`` file, also in the repo's root.


Python Libraries
****************

If working with containers, the dependencies should all be installed (generally from PyPI), here we discuss briefly those features enabled by each.


Required
--------

The following dependencies are required for core functionality and thus non-optional.

`PyYAML <http://pyyaml.org>`_ is used to read yaml formatted configuration files.

`asteval <https://newville.github.io/asteval/>`_ is used to process python statements presented as strings (sometimes provided as strings in start-up configurations or as part of calibration definitions).


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

`ipython <http://ipython.org>`_ and `ipdb <http://www.pypi.python.org/pypi/ipdb>`_ are both highly recomended for all non-production workflows.
The expanded tab completion, command and output history, and doc access make it a powerful python interpretor for developing or manually interacting with dripline components.

