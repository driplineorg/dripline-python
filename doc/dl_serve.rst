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

.. code-block:: yaml

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
    module: Service
    module_path: <provide module path (optional)>

    endpoints:
      - name: <endpoint 1 name>
        module: <endpoint 1 module>
        module_path: <endpoint 1 module path (optional)>
        <other endpoint 1 parameters>
      - name: <endpoint 2 name>
        module: <endpoint 2 module>
        module_path: <endpoint 2 module path (optional)>
        <other endpoint 2 parameters>
      <...>

Any paramters for which you want to use the default values can be left out of the configuration file and do not 
need to be specified in other ways (e.g. with a command-line option).  The parameters in angle brackets (``<>``) 
do not have default values because they'll be specific to the service and will need to be provided by the user.

When starting the service, ``module`` and ``module_path`` are used to create the service object, while 
the remaining configuration information is provided as keyword arguments to the service's ``__init__()`` function.

.. note::
    As a matter of convention, dripline-python classes all accept extra keyword arguments to their ``__init__`` functions, usting the ``**kwargs`` argument packing.
    These are passed along when the class calls the ``__init__`` of its base class(es), allowing the complete set of keyword arguments to be provided.

.. note::
    Whenever possible, dripline-python classes provide default values to keyword arguments so that derrived classes are able to be created given the above convention.
    All required arguments of the class and its base classes must be passed to the ``__init__`` of any class (for example, ``Endpoint``, which is a base of all available classes, requires the ``name`` keyword argument, meaning that every instance node must have a name argument).

For a complete example of configuring a service, please see the :doc:`controls-guide:guides/first-mesh`.

Module and Module Path
----------------------

The class used by the application is specified as the ``module`` in the configuration.  The default is ``dripline.core.Service``, 
and the class used should be ``Service`` or a class derived from it.
Any service class in the ``dripline`` namespace can be used, including those in ``dripline.core`` and ``dripline.implementations`` within the 
dripline-python repo, and ``dripline.extensions`` for any :doc:`Dripline extension modules</extending>`.  

For modules outside of the ``dripline`` namespace, the module path can be provided with the ``module_path`` key.  
If present, this file is searched first and so it will take precedent if the ``module`` has the same name 
as a class which is part of dripline-python or any extension.

Endpoints
---------

Endpoints are provided as a list of endpoint configurations under the ``endpoints`` key.  As with the service, 
the ``module`` and ``module_path`` parameters are used to create each endpoint object, and the remaining parameters 
in each block is provided to the respective endpoint's ``__init__()`` function.

Configuration File
------------------

For most uses of ``dl-serve``, most of the configuration information (other than the defaults) will be provided in a configuration file.  

.. tip::
    To maximize the ability to reuse configuration files in different meshes, we suggest that mesh configuration details be provided in a :ref:`:ref: .dripline_mesh.yaml <dripline-cpp:default-mesh-yaml>`` file, 
    and the service configuration file be specific to the particular service.

Here is an example service configuration file:

.. code-block:: yaml

    name: my_store
    module: Service
    endpoints:
      - name: peaches
        module: KeyValueStore
        calibration: '2*{}'
        initial_value: 0.75
        log_interval: 10
        get_on_set: True
        log_on_set: True
      - name: chips
        module: KeyValueStore
        calibration: 'times3({})'
        initial_value: 1.75
      - name: waffles
        module: KeyValueStore
        calibration: '1.*{}'
        initial_value: 4.00

Parameter Keywords
------------------

For the most part, any YAML- or JSON-valid key name can be used for a configuration parameter key, and it has to match the 
keyword argument key in the relevant class's ``__init__()`` function.

There are several reserved keywords:

* ``name`` -- every endpoint (and service, since a service is an endpoint) has a name parameter that must be unique across the mesh.
* ``module`` -- the class name that will be built
* ``module_path`` -- an optional parameter to specify the path to the Python module containing the class, if it's not within the ``dripline`` namespace.

Authentication
==============

Communication with the RabbitMQ broker requires user/password authentication.

See :doc:`dripline-cpp:authentication` for information on how to specify the authentication information.
