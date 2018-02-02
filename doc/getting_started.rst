===============
Getting Started
===============

System Requirements
*******************
The development of dripline is being done primarily on OS X (with packages installed via homebrew and python packages through pip) and debian linux (with any system-packages from apt and python pacakges through pip).

We have made no attempt to determine the exact minimal system requirements, but develop primarily in python 2.7 with "current" versions of dependencies from PyPI.
No effort is made to maintain compatibility with python < 2.7; the code should be compatible with python 3.x and we hope to transition to primarily (and possibly exclusively) python 3 usage in the future.

Installation
************

There are two recommended approaches to installation and use of dripline-python.
Using docker containers can take more setup but eliminates the need for any installation steps and is useful for integrated development.
The docker approach is preferred for Project 8 collaborators, especially when working within the context of the rest of our controls software ecosystem.
Virtual environments allow for mostly local installation and development; they are common in the python community.

Docker containers
-----------------

The easiest way to get started with docker is simply to use the container image from the `dockerhub repository <https://hub.docker.com/r/project8/dripline-python/>`_.
You may also use the ``Dockerfile`` located in the dripline-python GitHub repository's root directory to build the image yourself (the full repository is the required build context).

Virtual Environments
--------------------

The recommended usage is with a `virtual environment <http://virtualenv.readthedocs.org/en/latest>`_ and the `ipython <http://ipython.org>`_ interpreter.
Assuming you have virtualenv installed (On debian, you can install it from your package manager; on Mac you should install pip from homebrew, then use pip to instal virtualenv) it is relatively simple to get everything going.
For the complete experience, you would run the following three commands (the last line installs all recommended extras, you can include any combination or none of them).

.. code-block:: bash

    $ virtualenv path/to/virt_environments/dripline [--system-site-packages]
    $ source path/to/virt_environments/dripline/bin/activate
    $ pip install -e . [doc,database,other]


This will install the local dripline source into your same virtual environment. If you are going to develop on the source replace the last line with the following two:

.. code-block:: bash

    $ pip install pika msgpack-python PyYAML [whichever optionals you want]
    $ python setup.py develop

That will install the dependencies, and create symbolic links for the dripline python files.
This way as you make changes to the source you don't have to rerun the ``$ python setup.py install`` step.
More details can be found in the documentation for python's `setup tools <http://pythonhosted.org//setuptools/>`_.


Python Libraries
****************
There are quite a few dependencies for dripline, some required and many optional (though needed for certain features).
Unless otherwise noted, you are encouraged to install any/all of these from PyPI using pip.

Required
--------

The following dependencies are required for core functionality and thus non-optional.

`Pika <http://pika.readthedocs.org>`_ is an amqp library.

`PyYAML <http://pyyaml.org>`_ is used to read yaml formatted configuration files.
It could in principle (and perhaps should) be moved to "optional" status (since it is possible to run several aspects without a config file, and json based config files would be easy to use.
Nevertheless, PyYAML is pervasive and we've had no motivation to refactor to make it cleanly optional.

`asteval <https://newville.github.io/asteval/>`_ is used to process python statements presented as strings (sometimes provided as strings in start-up configurations or as part of calibration definitions).

Building Docs [doc]
~~~~~~~~~~~~~~~~~~~

`Sphinx <http://sphinx-doc.org/>`_ is required to compile this documentation.

`Sphinx-rdc-theme <https://github.com/snide/sphinx_rtd_theme>`_ is used by Sphinx for a nicer look.

.. `Sphinx-contrib-programoutput <http://pythonhosted.org/sphinxcontrib-programoutput/>`_ Is used to automatically include the --help for the various utility programs.

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

.. `virtualenv <http://virtualenv.readthedocs.org/en/latest>`_ provides a clean way to install python libraries without polluting the system python install (or if you don't have permission to modify the system).



