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

The official definition of the dripline protocol can be found on the `the dripline repository <https://github.com/project8/dripline>`_ available also `rendered <https://dripline.readthedocs.io/en/latest/>`_.

