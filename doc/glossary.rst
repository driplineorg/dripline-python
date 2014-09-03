.. _parlance:

########
Glossary
########

.. glossary:: :sorted:

    producer
        An application or other process which is integrated with rabbitmq. A producer may have zero or more associated :term:`endpoint` objects attached.

    endpoint
        A logical destination in the slow control sysem, generally one which is physically meaningful. The pressure or temperature reading for a particular instrument for example. These are very similar to the "channels" concept previously.

    node
        A node referrs to a server or other physical device which is part of the :term:`mesh` and hosts any number of :term:`producer` and/or client applications.

    mesh
        The complete set of components in a slow control system. It is centered around an AMQP server (such as rabbitmq) and referrs to everything connected to it.
