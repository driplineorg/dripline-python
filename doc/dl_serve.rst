================
Dripline Service
================

Dripline includes an executable for running a dripline service defined in a YAML configuration file.
The configuration file defines the set of class instances which will make up the service, as well as their initial configurations.
The tool will create those instances and start the main execution loop.

.. TODO sphinx supports autodoc for the CLI tools. We should consider replacing the following code blocks with parsed CLI output from `--help` in the future (if we're building in an environment where dripline-cpp is installed).

Use
===

  ``> dl-serve [options] [keyword arguments]``

The user typically provides a configuration file with the ``-c`` (``--config``) option.

Options
-------

::

  -h,--help                   Print this help message and exit
  -c,--config TEXT:FILE       Config file filename
  --config-encoding TEXT      Config file encoding
  -v,--verbose                Increase verbosity
  -q,--quiet                  Decrease verbosity
  -V,--version                Print the version message and exit
  -u,--username TEXT          Specify the username for the rabbitmq broker
  --password TEXT             Specify a password for the rabbitmq broker -- NOTE: this will be plain text on the command line and may end up in your command history!
  --password-file TEXT        Specify a file (e.g. a secrets file) to be read in as the rabbitmq broker password
  --auth-file TEXT            Set the authentication file path
  -b,--broker TEXT            Set the dripline broker address
  -p,--port UINT              Set the port for communication with the dripline broker
  --requests-exchange TEXT    Set the name of the requests exchange
  --alerts-exchange TEXT      Set the name of the alerts exchange
  --max-payload UINT          Set the maximum payload size (in bytes)
  --heartbeat-routing-key TEXT
                              Set the first token of heartbeat routing keys: [token].[origin]
  --max-connection-attempts UINT
                              Maximum number of times to attempt to connect to the broker
  --loop-timeout-msloop_timeout_ms UINT
  --message-wait-msmessage_wait_ms UINT
  --heartbeat-interval-s UINT Set the interval between heartbeats in s


Configuration
=============

For information applicable to all dripline application configurations, see :doc:`dripline-cpp:configuration`.

The full configuration for a service, with default values, is:

.. code-block:: YAML
   dripline_mesh : 
     alerts_exchange : alerts
     broker : localhost
     broker_port : 5672
     heartbeat_routing_key : heartbeat
     max_connection_attempts : 10
     max_payload_size : 10000
     requests_exchange : requests
   
   enable_scheduling : true
   heartbeat_interval_s : 60
   loop_timeout_ms : 1000
   message_wait_ms : 1000

   name : dlpy_service
   module: <provide module>
   module-path: <provide module path (optional)>

   endpoints:
     <first endpoint>:
       name: <endpoint 1 name>
       module: <endpoint 1 module>
       module-path: <endpoint 1 module path (optional)>
     <second endpoint>:
       name: <endpoint 2 name>
       module: <endpoint 2 module>
       module-path: <endpoint 2 module path (optional)>
     <...>

Any paramters for which you want to use the default values can be left out of the configuration file and do not 
need to be specified in other ways (e.g. with a command-line option).  The parameters in angle brackets (``<>``) 
do not have default values because they'll be specific to the service and will need to be provided by the user.



Authentication
==============

Communication with the RabbitMQ broker requires user/password authentication.

.. TODO update the link to use "latest" symbolic link, or main/develop, when that is available

See `Authentication in the dripline-cpp docs <https://driplineorg.github.io/dripline-cpp/branches/dl3_develop/authentication.html>`_ for information on how to specify the broker and authentication information.

Configuration File
==================

The configuration is used to define what components are part of the service.
These elements all exist within the top-level ``runtime-config`` node within the configuration file, which is described here.
If not already familiar, you're encouraged to review the `dripline-cpp core library documentation <https://driplineorg.github.io/dripline-cpp/branches/dl3_develop/library.html>`_ for descriptions of roles of the base classes and their relationships.

.. TODO again, update this link to a more generic branch, when available.

The ``runtime-config`` node is built up out of nodes which each describe a class instance.
The details for defining instance nodes is below
The top level of the runtime configuration must be exactly one instance which is either a ``Service`` or a class derrived from it.
It follows the description below for any instance node, but has an extra reserved keyword (``endpoints``), which contains an array of instance nodes which will be added as children of the ``Service`` instance, these can be instance of any ``Endpoint``-derrived class.

For a more complete example of writing a configuration file and using it, see the `first mesh tutorial in the driplineorg controls guide<https://driplineorg.github.io/controls-guide/develop/guides/first-mesh.html>`_

Instance node description
-------------------------
Each instance node defines an object which will be created and configured as part of the service.
There are a number of reserved keywords, which are removed from the node before creation.
The rest of the node is unpacked into the named arguments of the ``__init__`` method of the class when it is created.
The reserved keywords are

.. glossary::

   module
      Specifies the name of the class to create an instance of.
      The application will search for a class with this name in the following namespaces in order and create the first one it finds:

      #. the source file provided in the ``module_path``, if provided
      #. the extensions namespace or any namespaces within the extensions namespace (this is not recursive beyond that level)
      #. the dripline.implementations namespace
      #. the dripline.core namespace

   module_path
      Path to an extra source file containing class implementation for the module.
      If present, this file is searched first and so it will take precidents if the ``module`` has the same name as a class which is part of dripline-python

.. note::
   As a matter of convention, dripline-python classes all accept extra keyword arguments to their ``__init__`` functions, usting the ``**kwargs`` argument packing.
   These are passed along when the class calls the ``__init__`` of its base class(es), allowing the complete set of keyword arguments to be provided.

.. note::
   Whenever possible, dripline-python classes provide default values to keyword arguments so that derrived classes are able to be created given the above convention.
   All required arguments of the class and its base classes must be passed to the ``__init__`` of any class (for example, ``Endpoint``, which is a base of all available classes, requires the ``name`` keyword argument, meaning that every instance node must have a name argument).
