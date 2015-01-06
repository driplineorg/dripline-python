Getting Started
===============

Libraries
*********
There are quite a few dependencies for dripline, some required and many optional (though needed for certain features).

Required
--------

`Pika <http://pika.readthedocs.org>`_ is an amqp library for python 2 (not 3.x).

`msgpack <http://msgpack.org>`_ is used to store payloads in messages transferred via amqp.

Optional
--------

`PyYAML <http://pyyaml.org>`_ is used to read yaml formatted configuration files.
While not required, configuration input files are used heavily and so it will be needed in nearly all cases.

`SQLAlchemy <http://www.sqlalchemy.org>`_ is used to talk to our postgresql database.
It is only required for builds which will be used to log sensor values.
For use with postgres, it requires **I need to look this up** which usually needs to be installed via package manager as it is not pure python and wraps other language library files.

`Colorlog <http://pypi.python.org/pypi/colorlog>`_ is completely aesthetic.
The logging module is used throughout dripline and this allows for colorized format of log messages.

Helpful Python Packages
-----------------------

`ipython <http://ipython.org>`_ is not actually a dependency at all, but is highly recommended.
The expanded tab completion, command and output history, and doc access make it a powerful python interpretor for developing or manually interacting with dripline components.

`virtualenv <http://virtualenv.readthedocs.org/en/latest>`_ provides a clean way to install python libraries without polluting the system python install (or if you don't have permission to modify the system).

For Building Documentation
--------------------------

`Sphinx <http://sphinx-doc.org/>`_ is required to compile this documentation.

`Sphinx-rdc-theme <https://github.com/snide/sphinx_rtd_theme>`_ is used by Sphinx for a nicer look.

`Sphinx-contrib-programoutput <http://pythonhosted.org/sphinxcontrib-programoutput/>`_ Is used to automatically include the --help for the various utility programs.

To build this documentation, you also need `sphinx <http://sphinx-doc.org/>`_ and `sphinx_rtd_theme <https://github.com/snide/sphinx_rtd_theme>`_.
All three can be obtained through `pip <http://pip.readthedocs.org/en/latest/installing.html>`_.


External
--------
`AMQP <http://www.amqp.org>`_ is completely external to dripline.
One such service must be operating or dripline components will have no means to communicate.
If developing for dripline, you are encouraged to install your own broker so that you can test locally.
The slow control administrator must maintain this service for use in the production system, others shouldn't need to interact with it other than to provide the host url to services.
Dripline is developed with `rabbitMQ <https://www.rabbitmq.com>`_ and a standard install of that service is recommended.
Other AMQP systems make work but are untested.

Operating System & Python
*************************
The development of dripline is being done on OS X and various linux systems.
While running on windows or other operating systems may be possible, the author's make no promise or offer of support.
Similarly, the expected versions of python are 2.7.3 and >= 3.3.0.
We will try to keep the codebase compatible with both, but use of older versions is untested and not guaranteed to work.


Prepare an Environment
----------------------

The recommended usage is with a `virtual environment <http://virtualenv.readthedocs.org/en/latest>`_ and the `ipython <http://ipython.org>`_ interpreter.
Assuming you have virtualenv installed (most likely available in the package manager for your system) it is relatively simple to get everything going.
For the complete experience, you would run the following three commands (the last line installs recommended extras).::

$ virtualenv path/to/virt_environments/dripline
$ source path/to/virt_environments/dripline/bin/activate
$ pip install pika PyYAML msgpack-python sqlalchemy
$ pip install ipython sphinx sphinx_rtd_theme sphinxcontrib-programoutput colorlog
.. sphinx-argparse is not used for now


Note that sphinx is only required if you want to (re)build this documentation and sphinx_rtd_theme is purely cosmetic.
Similarly, ipython is nice for the user but does not change available dripline features.

If you just want to run dripline you would run the following commands:

.. code-block:: bash

		$cd /path/to/dripline/repo
		$cd python
		$python setup.py  install

This will install the local dripline source into your same virtual environment. If you are going to develop on the source replace the last line with 

.. code-block:: bash
		
		$ python setup.py develop

That will install the local dripline source into your same virtual environment rather than actually installing. This way as you make changes to the source you don't have to rerun the 
$ python setup.py install 
step. More details can be found in the documentation for python's `setup tools <http://pythonhosted.org//setuptools/>`_.  


First Steps
-----------
To get started, we will follow the example of connecting a simple 
endpoint to the broker which provides a random number generator.  We will
make a request to this endpoint using a dripline client.

Dripline uses `YAML <http://www.yaml.org/>`_ formatted files as its 
configuration file format.  In the `examples` directory of the dripline
source tree, you will find a file called ``random_node.yaml`` which should
look like this:

.. code-block:: yaml

    broker: localhost
    nodename: random_node
    providers:
    - name: local
      endpoints:
      - name: rng
        module: random_float

When this configuration file is loaded by dripline, it will construct an 
`object graph` from the list of providers and endpoints that appear.  This
particular configuration file tells dripline that we wish to construct an
object graph that has an endpoint named ``rng`` whose behavior can be found
in a module tagged as ``random_float`` (more on this later).  That endpoint
belongs to a provider called ``local``.  The name for the dripline node that
will be started is ``random_node``, and the node will try to connect to
an AMQP broker running on ``localhost``.

On that note, you need an AMQP broker running to run the example code.  Install
an instance of RabbitMQ server to the host of your choice, and start it.  No
configuration is necessary at all - dripline will take care of the rest.

To start the node which is providing the random number generating service,
simply do the following from the examples directory:

.. code-block:: bash

    $ ./rng_demo_node.py

Now, to start the client which will request a single random number and print it
to the screen, do

.. code-block:: bash

    $ ./rng_demo_client.py

You should see some log entries about connections, and a random floating point
number between 0 and 1!
