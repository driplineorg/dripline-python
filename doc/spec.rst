Specifications
==============

Abstractions
------------
* **Nodes**: are simply programs which implement the dripline protocol.

* **Messages**: are sent between nodes. Messages are structured data and fall into one of four types:
    * A **Request** from a node is directed to a particular recipient, called an **endpoint**.
    * A **Reply** is generated in response to a *specific* request. The request/reply pair is therefore a point-to-point communication pattern.
    * **Info** messages are intended to convey general information to nobody in particular. These messages should contain information related to the normal operation of the system, such as a node joining the dripline mesh.
    * An **Alert** is a message which is sent to anybody who is interested, and does not have a specific recipient. Alerts are intended to carry information related to a condition of the system, such as the value of a sensor exceeding a threshold or similar.

* **Endpoints**: are conceptually the destination of requests. Endpoints are hosted by nodes, and a node may be responsible for many endpoints. Endpoints are uniquely named by a single string which may contain any alphanumeric character, underscores, or hyphens; but which may *not* contain periods or commas (*i.e.* matching the regular expression ``^[a-zA-Z0-9_][^[.,]]*$``. A *request* is directed toward a particular endpoint, the *target*, and the node which hosts that endpoint is responsible for delegating the request.
    * **Services** are endpoints that perform some task. For example, the digitizer DAQ may expose some service called *e.g.* ``take_data`` which begins an acquisition.
    * **Sensors** are endpoints that read some physical value in the system. For example, this may be a pressure or a voltage.
    * **Monitors** (not currently implemented) are endpoints which monitor the status of nodes to detect failures.

* **Groups** (not implemented) can be used to form logical groupings of endpoints into a single endpoint. For example, two channels ``bore_pressure`` and ``source_pressure`` could be grouped into a logical endpoint called ``pressure``.

Messages
--------

The wire format for messages is MessagePack. The message structure is simple:

* ``msgtype::integer``
    The type of the message, which is (see above) either Reply(2), Request(3), Alert(4), or Info(5). This field *must* be defined for every message sent.

* ``msgop::integer``
    The operation to perform. This field need only be defined for messages with msgtype set to Request

* ``target::string``
    The target endpoint for a request.

* ``timestamp::string``
    A timestamp for the message in `RFC3339 <https://www.ietf.org/rfc/rfc3339.txt>`_ format. The sender of the message is responisible for setting this. It *must* be attached to every message.
* ``payload::any``
    Data which is attached to the message. This may be of any type.
* ``exceptions:: any``
    Any error or information that is generated during the processing of a request. This may be set for any message.
