===================================
Introduction and Background Reading
===================================

Before delving into the details of dripline, there is some important context to discuss.
These are generally beyond the scope of even this page, but I'll try and point you in the right direction before assuming you know what's going on.

Advanced Message Queuing Protocol (AMQP)
========================================

`AMQP <http://www.amqp.org>`_ is a specification for a centralized message routing system, and it is important to note that it refers to the *specification* and not a particular *implementation*.
All current use and development of dripline is currently being done with the `RabbitMQ <http://www.rabbitmq.com>`_ implementation of AMQP.
We use a vanilla installation of version 2.8.4 of rabbit from the Debian Linux 7.7 (note that we plan to upgrade to Debian 8 "jessie" eminently).

By using a centralized message routing service, it becomes easy for services to be run on as many different systems as we like.
We can also add and remove services from the system without having to disrupt others, etc.

.. _wire-protocol:

Message Wire Protocol
=====================
If AMQP defines a protocol for message routing, the Project 8 wire protocol defines a protocol for the content of those messages.
By having a standard that all messages follow, it is possible for any appropriately implemented application, regardless of host system, programming language, etc., to interact with any other successfully.
That is, as long as your C++ application on Windows and my python application on Linux are both speaking the same version of the Project 8 Wire Protocol over the same AMQP broker, they will get along just fine.

The *official* definition of the wire protocol can be found on the `Project 8 wiki <https://github.com/project8/hardware/wiki/Wire-Protocol>`_ (this page requires authentication to github and membership in the Project 8 organization).
I will duplicate that information here now, but assume it will immediately be out of date; please request (via email or github issue) an update to this information if you suspect it is stale.

.. literalinclude:: wire_protocol.txt

Dripline Payload Syntax
=======================
While the wire protocol allows for the payload field to be of any type, meaningful interactions must constrain this field.
Here I'll describe the standards expected by dripline for various message types.

Request Messages
++++++++++++++++

.. todo:: add request message standard

Reply Messages
++++++++++++++

.. todo:: add reply message standard

Alert Messages
++++++++++++++

.. todo:: add alert message standard
