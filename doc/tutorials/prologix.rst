A Single GPIB Instrument with Prologix
**************************************

This tutorial is for adding gpib devices to an existing dripline system.

A Hardware Review
-----------------
For this example, we'll consider the simple case of the Lecroy 9210 pulse generator being accessed via a prologix GPIB to ethernet controller.
Before we worry too much about dripline, we should understand some basics of how that hardware combination works.

The prologix controller is configured to a static IP address within the lab's internal network.
A single socket can be opened to the controller and packets sent to it.
Commands that begin with "++" are for the controller itself, others are passed along to the currently addressed GPIB device.
The details of this are taken care of by dripline.

The Lecroy 9210, like any GPIB device, uses SCPI commands for configuration and control.
By reading through the manual, we find many useful commands which we may want to add.
In this example, we will consider two:

    1) ``*IDN?`` is a command which instructs the device to return a comman separated list of identifying information (including make, model, serial number, etc.). It is used as a query, but does not accept configuration.
    2) A:WID is a command which sets the width of an output pulse in seconds. It supports both a query mode ``A:WID?`` and a configuration mode ``A:WID <value>``.

There are many further commands available for the 9210, they can be added in the same way as these two.

Configuring a Service
---------------------
All of the details of our configuration will be contained in a single YAML configuration file.
The hierarchical structure of our configuration file will reflect the physical and conceptual relation between the various abstractions in dripline.

The Service
+++++++++++
At the highest level, we will be running a single python application.
It is responsible for connecting to AMQP and dealing with communcation.
The service must be configured with a name, a network path to the amqp server, and a list of providers for which it is responsible (this last one comes in the next section).

We create a new configuration file and add that content, it should look like this:
(!!! I should be able to actually just ref line numbers in the source, rather than duplicate them in the rst...)

.. literalinclude:: ../../examples/prologix_lecroy.yaml
    :language: yaml
    :lines: 1-2
    :emphasize-lines: 1-2

Here I've named the service prologix_tutorial, since that's what we're doing.
I've set broker to localhost, this implies that there is an amqp server running on my local system.

Prologix Controller
+++++++++++++++++++
Our service will own one provider, a single prologix controller.
We therefore add a (one element long) list of providers to the above servce, with the requisite configuration details.

.. literalinclude:: ../../examples/prologix_lecroy.yaml
    :language: yaml
    :lines: 1-6
    :emphasize-lines: 3-6

Note that in addition to a name, I've assigned configuration values for module and socket_info.
The module is the name of a class within dripline.instrument (that should be linked) which our service will create.
Any keyworded arguments for that class's __init__() may be specified in the same way that here I've set the socket_info.

Pulser Instrument
+++++++++++++++++
Now that we have the controller itself configured we want to add and configure the instrument(s) attached to it.
In this example, that is another one element list with only the Lecroy 9210.
That now looks like:

.. literalinclude:: ../../examples/prologix_lecroy.yaml
    :language: yaml
    :lines: 1-10
    :emphasize-lines: 7-10

Hopefully the pattern is starting to be clear.
There is a name assigned to the instrument, and a module which is another class in dripline.instrument.
Again from it's __init__(), we've specified the value of addr (the GPIB address of the pulser).

Endpoints
+++++++++
Finally, we'll add the actual commands that we want to be able to access via the slow controls.
They follow the same pattern as the last two.

.. literalinclude:: ../../examples/prologix_lecroy.yaml
    :language: yaml
    :lines: 1-20
    :emphasize-lines: 11-20

And there we have it, a configuration to let us remind ourselves just what the pulser is, and set how long the pulses last.
To start it we use the :ref:`open_spimescape_portal` utility script, if everything works, it should look something like:

.. literalinclude:: open_portal_output.log
    :language: bash

You can then open another terminal and interact with your endpoints:

.. code-block:: bash

    $ dripline_agent -b myrna.local get tickler_pulse_width
    tickler_pulse_width: 1.00000E-3


Logging
-------
Next we enable the logger(s) and see their outputs using the message monitor.

Finally the logger service is started and values stored to postgres.
