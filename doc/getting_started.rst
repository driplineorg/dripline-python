Getting Started
===============

Dependencies
------------
To use the python interface to dripline, you will need three dependencies:

* pika >= 0.9.8
* msgpack-python >= 0.4.2
* pyyaml >= 3.11

All of these are available via `pip install package`

*Note*:
The steps above will give you a fully functioning dripline client, but
without a message broker to communicate with, the client won't do you much
good.  We recommend using a standard AMQP broker such as 
`RabbitMQ <https://www.rabbitmq.com>`_

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