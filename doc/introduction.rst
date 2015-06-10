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
