===============
Getting Started
===============

Actually installing dripline is quite easy, but has various dependencies disccused in following section.
The recommended installation procedure follows that discussion.

System Requirements
*******************
The development of dripline is being done primarily on OS X (with packages installed via homebrew and python packages through pip) and debian linux (with packages obviously from pip and python pacakges through pip).

.. todo:: list dependency lib versions known to work

We have made no attempt to determine the minimal system requirements, but develop primarily in python 2.7 with "current" versions from PyPI.
No effort is made to maintain compatibility with python < 2.7; the code should be compatible with python 3.x but since pika isn't available for python 3, that is untested.

Python Libraries
****************
There are quite a few dependencies for dripline, some required and many optional (though needed for certain features).
Unless otherwise noted, you are encouraged to install any/all of these from PyPI using pip.

Required
--------

`Pika <http://pika.readthedocs.org>`_ is an amqp library for python 2 (not 3.x).

`msgpack <http://msgpack.org>`_ is used to store payloads in messages transferred via amqp.

`PyYAML <http://pyyaml.org>`_ is used to read yaml formatted configuration files.
It could in principle (and perhaps should) be moved to "optional" status (since it is possible to run several aspects without a config file, and json based config files would be easy to use.
Nevertheless, PyYAML is pervasive and we've had no motivation to refactor to make it cleanly optional.

Optional
--------
Various optional features can be activated by installing one or more extra dependencies.
You may install them directly using pip, or list the optional extras (named in []) when issuing a setuptools install.

Databases [database]
~~~~~~~~~~~~~~~~~~~~
`SQLAlchemy <http://www.sqlalchemy.org>`_ is used to talk to our database.
This is nice because it supports a wide range of databases and backends for them.
In the future, if we elect to change our database, this will hopefully minimize the number of changes we'll need to make.

`psycopg2 <http://initd.org/psycopg>`_ is a PostgreSQL adapter and provides a SQLAlchemy backend by wrapping libpq (the official PostgreSQL client).
Per the `psycopg2 documentation <http://initd.org/psycopg/docs/install.html#installation>`_, you are encouraged to install psycopg2 using your package manager (it should be available from homebrew for Mac users).
If you do so, and are using a virtualenv (and if you're not, why aren't you), you'll need to create your virtualenv with the ``--system-site-packages`` flag, otherwise it won't be found.

Building Docs [doc]
~~~~~~~~~~~~~~~~~~~

`Sphinx <http://sphinx-doc.org/>`_ is required to compile this documentation.

`Sphinx-rdc-theme <https://github.com/snide/sphinx_rtd_theme>`_ is used by Sphinx for a nicer look.

`Sphinx-contrib-programoutput <http://pythonhosted.org/sphinxcontrib-programoutput/>`_ Is used to automatically include the --help for the various utility programs.

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

`virtualenv <http://virtualenv.readthedocs.org/en/latest>`_ provides a clean way to install python libraries without polluting the system python install (or if you don't have permission to modify the system).


Prepare an Environment
**********************

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
