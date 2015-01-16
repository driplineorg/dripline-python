A Dripline powered key-value store
**********************************
As a way to explore how dripline creates sensors that we can interact with
via the dripline protocol, let's create and interact with a simple example:
a key-value store which is implemented as a dripline endpoint.  The key-value
store will be very simple: a list of keys, each of which is a string (for
example, ``key0``, ``foo_key``, ``some_name``, whatever).  Associated with 
each key is a floating point number which is its value: 1.3 perhaps, or -3.4, 
or 1.4e21, or really anything that can represent a floating point number.  
What we want as a user is some remote storage for such a key-value store, where
we can ask dripline for the current value of ``key0`` and have it answer with
whatever that current value may be.  


A quick refresher
-----------------
First let's recall how things are structured in a dripline 
node.  The most basic functional unit in a dripline node is an *endpoint*.
An endpoint represents something that we want to interact with - perhaps it is
the contents of some file in a directory, or the input to a voltmeter, or 
in this case, a value associated with some key.  In a dripline configuration
file, an endpoint is always declared in a block whose name is ``endpoints``.

**Every** endpoint must have a *provider* associated with it.  The concept
of a provider represents an element in the system without which an endpoint
could not independently function.  For example, consider a case where an
endpoint represents the input to a digital voltmeter which is connected to
an ethernet router.  Without a connection to the voltmeter, we clearly can't 
communicate with the endpoint.  For that reason, we may write some code which
performs the communication with the voltmeter itself, and then we say that
code *provides* the endpoint which is the input to the voltmeter.  It's also
the case that once we have one connection to the voltmeter, it seems like 
wasted effort to duplicate that among many objects, and so the voltmeter 
provider can act as a logical way to group endpoints together.  

Let's go
--------
To start with, let's consider the structure of our key-value store.  We
have a list of some keys that have string names, and each key has a floating
point value associated with it.  We will consider a list of items at a store,
each of which has a price in dollars.  It's not a very big store - we only
have peaches, chips, and waffles.  The prices of these items fluctuates a lot
due to global waffle demand, and so we want to be able to both ask our system 
what the current price is, and change the prices as necessary.  

The dripline ``kv_store`` provider and ``kv_store_key`` endpoint will give us
exactly this in a very simple way.  If the current pricelist is something like

* Peaches: 0.75
* Chips: 1.75
* Waffles: 4.00

We can write a configuration file for dripline (note, this exact file is in ``
examples/kv_store_tutorial.yaml``) that looks like this and represents our
pricelist in a very recognizable way:

.. code-block:: yaml

  nodename: my_store
  broker: localhost
  providers:
    - name: my_price_list
      module: kv_store
      endpoints:
        - name: peaches
          module: kv_store_key
          initial_value: 0.75
        - name: chips
          module: kv_store_key
          initial_value: 1.75
        - name: waffles
          module: kv_store_key
          initial_value: 4.00

That's it.  The ``nodename`` parameter is simply telling dripline that we want
our dripline node to be called ``my_store``.  The ``broker`` is telling 
dripline that there is an AMQP router which is installed on localhost.  
In the ``providers`` section, we declare a provider named ``my_price_list``, 
with the ``module`` parameter set to ``kv_store``.  When dripline sees the 
``module`` parameter, it will look to see what that string value corresponds to
in terms of the object that it should construct.  In this case, it will 
construct an object of type ``KVStore`` and give it the name ``my_price_list``.
The ``endpoints`` of ``my_price_list`` correspond to the prices of each
individual item.  Each endpoint has a ``name``, which is simply the name of the
item, and a ``module``, which is identical to the idea of a provider module.

The only new thing here is the ``initial_value`` parameter, which you notice
is equal in each case to the initial price of the object of the same name
as the endpoint.  Dripline considers every parameter which isn't called 
``name`` or ``module`` to be *specific to the object* and passes it along to
the object for it to do with as it likes.  In this instance, the initializer
of the ``KVStoreKey`` object looks like this:

.. code-block:: python

 def __init__(self, name, initial_value=None):
        self.name = name
        self.provider = None
        self.initial_value = initial_value

Note that initial_value is a keyword argument to the constructor, which sets
whatever that parameter may be to be the initial value associated with the
key.  

Interacting with it
-------------------
OK, enough details.  To fire up our key-value store and start interacting with
it, we want to start a dripline node which will use our configuration file.
To do that, we will use :ref:`open_spimescape_portal` located in the bin directory.
We point it to our configuration file (if you are intrepid enough to make your
own, point to whatever you created), and fire it up:

.. code-block:: bash

  $ open_spimescape_portal -c examples/kv_store_tutorial.yaml -vvv

Notice the ``-vvv`` which sets the output to its most verbose. For each "v" you
omit, one logging severity level will be omited. If no ``-v`` option is given,
normal operation should produce no terminal output. If you do the above, you should
see output that looks like this:

.. literalinclude:: kv_store_service_startup_output.log
    :language: bash

This isn't too hard to follow - dripline starts up, connects to the broker
you told it to, adds a provider and the endpoints, and is ready to go.

Now let's start getting some prices.  We're going to use ``dripline_agent``
to do this, as it gives us a very easy way to interact with dripline 
endpoints from the command line.  First of all, let's check the current
price of peaches:

.. code-block:: bash

    $ dripline_agent -b localhost get peaches
    2014-09-08 13:45:57,905 - node - INFO - connecting to broker localhost
    peaches: 0.75

Nice.  So the current price of peaches in our store is 0.75.  What about
waffles?

.. code-block:: bash

    $ dripline_agent -b localhost get waffles
    2014-09-08 13:52:26,597 - node - INFO - connecting to broker localhost
    waffles: 4.0

If you have another computer on your local network (or any network that can see
your amqp broker) then you can do the same thing from there:

.. code-block:: bash
   
    (on_amqp_server) $ dripline_agent -vvv get waffles
    2015-01-15T13:00:30Z[INFO    ] dripline.core.node(22) -> connecting to broker None
    waffles: 4.0
    
    (on_some_other_server) $ dripline_agent -b <amqp.broker.server.address> get peaches
    peaches: 0.75

Note again that the ``-v`` option can be given to increase the output verbosity.

Now let's say that there's been a global rush on chips and the price we
have to charge has skyrocketed from 1.75 to 1.79.  We can use 
``dripline_agent`` to set the new value:

.. code-block:: bash

  $ dripline_agent -b localhost get chips
  2014-09-08 13:53:57,432 - node - INFO - connecting to broker localhost
  chips: 1.75
  
  $ dripline_agent -b localhost set chips 1.79
  2014-09-08 13:53:38,545 - node - INFO - connecting to broker localhost
  chips->1.79: complete
  
  $ dripline_agent -b localhost get chips
  2014-09-08 13:53:59,768 - node - INFO - connecting to broker localhost
  chips: 1.79
