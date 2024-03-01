==================
Extending Dripline
==================

Dripline-python can be conveniently extended using the namespace plugin method.  The controls-guide 
repository includes an example set of files that can be copied into a new repository to create 
an extension to the ``dripline`` namespace.  Please see the 
`controls-guide documentation <https://controls-guide.readthedocs.io/en/latest/>`_
to follow a walkthrough that will implement a new dripline extension.

Adding a Service Class
======================

Adding an Endpoint Class
========================

There are some situations in which you will need to create your own endpoint class to add functionality that's not 
available in the the ``core`` or ``implementations`` sub-packages.  A new endpoing class can be derived from 
``Endpoint``, ``Entity``, or any of the endpoint classes from ``dripline.implementations``.

Adding ``CMD`` Handlers
~~~~~~~~~~~~~~~~~~~~~~~

The default behavior for dripline-python endpoints (as implemented in ``Endpoint``) is for any function attribute 
of an endpoint class to be addressable with an ``OP_CMD`` request.

We'll cover the primary features that will need to be addressed, followed by an example that 
will illustrate everything.

**Basic Setup**

.. code-block:: python

    def my_cmd(self, [args], [**kwargs])
        [do something]
        return [a variable]

This can be addressed with ``dl-agent`` by an ``OP_CMD`` request::

    dl-agent cmd an_endpoint -s my_cmd [args] [kwargs]

**Arguments**

The function can include both positional arguments and keyword arguments.  Positional arguments 
would be defined as:

.. code-block:: python

    def concatenate(self, an_arg1, an_arg2):
        return repr(an_arg1) + repr(an_arg2)

and addressed with ``dl-agent`` as::

    dl-agent cmd an_endpoint -s concatenate "My number is " 5

The return value would be ``My number is 5``.

Keyword arguments would be defined as:

.. code-block:: python

    def make_list(self, a_kwarg1, a_kwarg2=100):
        return [a_kwarg1, a_kwarg2]

and addressed with ``dl-agent`` as::

    dl-agent cmd an_endpoint -s make_list a_kwarg2=20000 a_kwarg1=1000 

The return value would be ``[1000, 20000]```.

**Return**

The return values can be null (returning ``None`` in Python), scalar values (integers, floats, or strings), 
array-like data (a list in Python), or dictionary-like data (a dict in Python).

**Example**

Endpoint definition:

.. code-block:: python

    class AnEndpoint(dripline.core.Entity):
        def __init__(self, base_str="The answer is: "):
            self.base = base_str

        def on_get(self):
            return self.base_str

        def on_set(self, new_value):
            self.base_str = new_value

        def concatenate(self, an_arg1, an_arg2):
            return self.base + repr(an_arg1) + repr(an_arg2)

        def make_list(self, a_kwarg1, a_kwarg2=100):
            return self.base + f"{[a_kwarg1, a_kwarg2]}
   
Usage (with ``dripline.core.Interface``):

.. code-block:: python

    import dripline.core.Interface as Interface
    ifc = Interface([config info])
    print( ifc.get('an_endpoint') )
    print( ifc.cmd('an_endpoint', 'concatenate', 'Hello, ', 'world') )
    ifc.set('an_endpoint', 'As a list: ')
    print( ifc.cmd('an_endpoint', 'make_list', a_kwarg1='Hello, ', a_kwarg2='world') )

The output should be::

    The answer is:
    The answer is: Hello, world
    As a list: ['Hello, ', 'world']
