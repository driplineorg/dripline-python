===============
Getting Started
===============

Libraries
*********
The required librares are `pika <pika.readthedocs.org>`_, `PyYAML <pyyaml.org>`_, and `msgpack <msgpack.org>`_.
To build this documentation, you also need `sphinx <http://sphinx-doc.org/>`_ and `sphinx_rtd_theme <https://github.com/snide/sphinx_rtd_theme>`_.
All three can be obtained through `pip <http://pip.readthedocs.org/en/latest/installing.html>`_.

*Note*:
The steps above will give you a fully functioning dripline client, but
without a message broker to communicate with, the client won't do you much
good.  We recommend using a standard AMQP broker such as 
`RabbitMQ <https://www.rabbitmq.com>`_

Operating System & Python
*************************
The development of dripline is being done on OS X and various linux systems.
While running on windows or other operating systems may be possible, the author's make no promise or offer of support.
Similarly, the expected versions of python are 2.7.3 and >= 3.3.0.
We will try to keep the codebase compatible with both, but use of older versions is untested and not guaranteed to work.


Prepare an Environment
----------------------

The recommended usage is with a `virtual environment <virtualenv.readthedocs.org/en/latest>`_ and the `ipython <ipython.org>`_ interpreter.
Assuming you have virtualenv installed (most likely available in the package manager for your system) it is relatively simple to get everything going.
For the complete experience, you would run the following three commands (the last line installs recommended extras).::

$ virtualenv path/to/virt_environments/dripline
$ source path/to/virt_environments/dripline/bin/activate
$ pip install pika PyYAML msgpack-python 
$ pip install ipython sphinx sphinx_rtd_theme sphinxcontrib-programoutput
.. sphinx-argparse is not used for now

Note that sphinx is only required if you want to (re)build this documentation and sphinx_rtd_theme is purely cosmetic.
Similarly, ipython is nice for the user but does not change available dripline features.


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
