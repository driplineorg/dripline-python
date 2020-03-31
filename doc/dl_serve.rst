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

The user provides a configuration file.

Options
-------

::

  -h,--help                   Print this help message and exit
  -c,--config TEXT:FILE       Config file filename
  --verbosity UINT            Global logger verosity
  -V,--version                Print the version message and exit
  -b,--broker TEXT            Set the dripline broker address
  -p,--port UINT              Set the port for communication with the dripline broker
  --auth-file TEXT            Set the authentication file path
  --requests-exchange TEXT    Set the name of the requests exchange
  --alerts-exchange TEXT      Set the name of the alerts exchange
  --max-payload UINT          Set the maximum payload size (in bytes)
  --loop-timeout-msdripline.loop-timeout-ms UINT
  --message-wait-msdripline.message-wait-ms UINT
  --heartbeat-routing-key TEXT
                              Set the first token of heartbeat routing keys: [token].[origin]
  --heartbeat-interval-s UINT Set the interval between heartbeats in s


Authentication
==============

Communication with the RabbitMQ broker requires the broker address and port, and user/password authentication.

.. TODO update the link to use "latest" symbolic link, or master/develop, when that is available
See `Authentication in the dripline-cpp docs <https://driplineorg.github.io/dripline-cpp/branches/dl3_develop/authentication.html>`_ for information on how to specify the broker and authentication information.

Configuration File
==================

The configuration is used to define what components are part of the service.
These elements all exist within the top-level ``runtime-config`` node within the configuration file,
which is described here.
.. TODO again, update this link to a more generic branch, when available.
If not already familiar, you're encouraged to review the `dripline-cpp core library documentation <https://driplineorg.github.io/dripline-cpp/branches/dl3_develop/library.html>`_ for descriptions of roles of the base classes and their relationships.

The ``runtime-config`` node is built up out of nodes which each describe a class instance.
The details for defining instance nodes is below
The top level of the runtime configuration must be exactly one instance which is either a ``Service`` or a class derrived from it.
It follows the description below for any instance node, but has an extra reserved keyword (``endpoints``), which contains an array of instance nodes which will be added as children of the ``Service`` instance.

Instance node description
-------------------------
