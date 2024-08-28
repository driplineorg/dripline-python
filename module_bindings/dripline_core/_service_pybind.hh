#ifndef DRIPLINE_PYBIND_SERVICE
#define DRIPLINE_PYBIND_SERVICE

#include "binding_helpers.hh"
#include "_service_trampoline.hh"

#include "core.hh"
#include "service.hh"

#include "param_binding_helpers.hh"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/iostream.h"



namespace dripline_pybind
{
    std::list< std::string>  export_service( pybind11::module& mod )
    {
        std::list< std::string > all_items;
        all_items.push_back( "_Service" );
        pybind11::class_< _service,
                          _service_trampoline,
                          dripline::core,
                          dripline::endpoint,
                          dripline::scheduler<>,
                          scarab::cancelable,
                          std::shared_ptr< _service >
                        >( mod, "_Service", "Service binding" )
/*            .doc(R"""(The primary unit of software that connects to a broker and typically provides an interface with an instrument or other software.

                The Service class is the implementation of the "service" concept in Dripline.
                It's the primary component that makes up a Dripline mesh.

                The lifetime of a service is defined by the three main functions:
                1. `start()` -- create the AMQP channel, create the AMQP queue, bind the routing keys, and start consuming AMQP messages
                2. `listen()` -- starts the heartbeat and scheduler threads (optional), starts the receiver thread, and waits for and handles messages on the queue
                3. `stop()` -- (called asynchronously) cancels the listening service

                The ability to handle and respond to Dripline messages is embodied in the `endpoint` class.  
                Service uses `endoint` in three ways:
                1. Service is an endpoint.  A service can be setup to handle messages directed to it.
                2. Service has basic child endpoints.  These are also called "synchronous" endpoints.  
                    These endpoints use the same AMQP queue as the service itself.  Messages send to the 
                    service and to the synchronous endpoints are all handled serially.
                3. Service has asynchronous child endpoints.  These endpoints each have their own AMQP 
                    queue and thread responsible for receiving and handling their messages.

                A service has a number of key characteristics (most of which come from its parent classes):
                * `core` -- Has all of the basic AMQP capabilities, sending messages, and making and manipulating connections
                * `endpoint` -- Handles Dripline messages
                * `listener_receiver` -- Asynchronously recieves AMQP messages and turns them into Dripline messages
                * `heartbeater` -- Sends periodic heartbeat messages
                * `scheduler` -- Can schedule events
                
                As is apparent from the above descriptions, a service is responsible for a number of threads 
                when it executes:
                * Listening -- grabs AMQP messages off the channel when they arrive
                * Message-wait -- any incomplete multi-part Dripline message will setup a thread to wait 
                *                 until the message is complete, and then submits it for handling
                * Receiver -- grabs completed Dripline messages and handles it
                * Async endpoint listening -- same as abovefor each asynchronous endpoint
                * Async endpoint message-wait -- same as above for each asynchronous endpoint
                * Async endpoint receiver -- same as above for each asynchronous endpoint
                * Heatbeater -- sends regular heartbeat messages
                * Scheduler -- executes scheduled events

                In addition to receiving messages from the broker, a user or client code can give messages directly to the service 
                using `process_message(message)`.)""")*/
            .def( pybind11::init< const scarab::param_node&,
                                  const scarab::authentication&,
                                  const bool
                                >(),
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg_v( "config", scarab::param_node(), "ParamNode()" ),
                  pybind11::arg_v( "auth", scarab::authentication(), "Authentication()" ),
                  pybind11::arg( "make_connection" ) = true/*,
                  R"""(
Extracts necessary configuration and authentication information and prepares the service to interact with the RabbitMQ broker. Does not initiate connection to the broker.
    Parameters
    ----------
    - a_config Dripline configuration object.  The `queue-mame` must be uique for each service.  The `broker` (and `broker-port` if needed) should be made appropriate for the mesh.  
        The other parameters can be left as their defaults, or should be made uniform across the mesh.
        - *Service parameters*
        - `queue-name` (string; default: dlcpp_service) -- Name of the queue used by the service
        - `enable-scheduling` (bool; default: false) -- Flag for enabling the scheduler
        - `broadcast-key` (string; default: broadcast) -- Routing key used for broadcasts
        - `loop-timeout-ms` (int; default: 1000) -- Maximum time used for listening timeouts (e.g. waiting for replies) in ms
        - `message-wait-ms` (int; default: 1000) -- Maximum time used to wait for another AMQP message before declaring a DL message complete, in ms
        - `heartbeat-interval-s` (int; default: 60) -- Interval between sending heartbeat messages in s
        - *Dripline core parameters*
        - `broker` (string; default: localhost) -- Address of the RabbitMQ broker
        - `broker-port` (int; default: 5672) -- Port used by the RabbitMQ broker
        - `requests-exchange` (string; default: requests) -- Name of the exchange used for DL requests
        - `alerts-exchange` (string; default: alerts) -- Name of the exchange used for DL alerts
        - `heartbeat-routing-key` (string; default: heartbeat) -- Routing key used for sending heartbeats
        - `max-payload-size` (int; default: DL_MAX_PAYLOAD_SIZE) -- Maximum size of payloads, in bytes
        - `max-connection-attempts` (int; default: 10) -- Maximum number of attempts that will be made to connect to the broker
        - `return-codes` (string or array of nodes; default: not present) -- Optional specification of additional return codes in the form of an array of nodes: `[{name: "<name>", value: <ret code>} <, ...>]`. 
                If this is a string, it's treated as a file can be interpreted by the param system (e.g. YAML or JSON) using the previously-mentioned format
    - a_auth Authentication object (type scarab::authentication); authentication specification should be processed, and the authentication data should include:
    - a_make_connection Flag for whether or not to contact a broker; if true, this object operates in "dry-run" mode
                  )"""*/
                )
/*            .def( pybind11::init< const std::string& a_name,
                                  const bool a_enable_scheduling,
                                  const std::string& a_broadcast_key,
                                  const unsigned a_loop_timeout_ms,
                                  const unsigned a_message_wait_ms,
                                  const unsigned a_heartbeat_interval_s,
                                  const bool a_make_connection,
                                  const pybind11::kwargs& kwargs
                                >(),
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg( "name" ) = "dlpy_service",
                  pybind11::arg( "enable_scheduling" ) = true,
                  pybind11::arg( "broadcast_key" ) = "broadcast",
                  pybind11::arg( "loop_timeout_ms" ) = 1000,
                  pybind11::arg( "message_wait_ms" ) = 1000,
                  pybind11::arg( "heartbeat_interal_s" ) = 60,
                  pybind11::arg( "make_connection" ) = true,
                  pybind11::arg( "kwargs" ) = {}
            )*/
                              // mv_ bindings
    /*        .def( pybind11::init( []( const pybind11::dict a_config,
                                      const std::string& a_name,
                                      const std::string& a_broker,
                                      const unsigned int a_port,
                                      const std::string& a_auth_file,
                                      const bool a_make_connection )
                                  { return new  _service( (scarab_pybind::to_param(a_config, true))->as_node(),
                                                          a_name,
                                                          a_broker,
                                                          a_port,
                                                          a_auth_file,
                                                          a_make_connection); },
                                  []( const pybind11::dict a_config,
                                      const std::string& a_name,
                                      const std::string& a_broker,
                                      const unsigned int a_port,
                                      const std::string& a_auth_file,
                                      const bool a_make_connection )
                                  { return new  _service_trampoline( (scarab_pybind::to_param(a_config, true))->as_node(),
                                                                     a_name,
                                                                     a_broker,
                                                                     a_port,
                                                                     a_auth_file,
                                                                     a_make_connection); }
                                ),
                   DL_BIND_CALL_GUARD_STREAMS,
                   pybind11::arg( "config"),
                   pybind11::arg( "name" ) = "",
                   pybind11::arg( "broker" ) = "",
                   pybind11::arg( "port" ) = 0,
                   pybind11::arg( "auth_file" ) = "",
                   pybind11::arg( "make_connection" ) = true
            )
*/
            .def_property( "enable_scheduling", &dripline::service::get_enable_scheduling, &dripline::service::set_enable_scheduling )
            .def_property_readonly( "alerts_exchange", (std::string& (dripline::service::*)()) &dripline::service::alerts_exchange )
            .def_property_readonly( "requests_exchange", (std::string& (dripline::service::*)()) &dripline::service::requests_exchange )
            .def_property_readonly( "sync_children", (std::map<std::string, dripline::endpoint_ptr_t>& (dripline::service::*)()) &dripline::service::sync_children )
            //TODO: need to deal with lr_ptr_t to bind this
            //.def_property_readonly( "async_children", &dripline::service::async_children )

            .def( "bind_keys",
                  &_service::bind_keys,
                  "overridable method to create all desired key bindings, overrides should still call this version",
                  DL_BIND_CALL_GUARD_STREAMS
                )
            .def( "bind_key",
                  // Note, need to take a service pointer so that we can accept derived types... I think
                  [](_service* an_obj, std::string&  an_exchange, std::string& a_key){return _service::bind_key(an_obj->channel(), an_exchange, an_obj->name(), a_key);},
                  pybind11::arg( "exchange" ),
                  pybind11::arg( "key" ),
                  "bind the service's message queue to a particular exchange and key",
                  DL_BIND_CALL_GUARD_STREAMS
            )
            .def( "start", &dripline::service::start, DL_BIND_CALL_GUARD_STREAMS )
            .def( "listen", &dripline::service::listen, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            .def( "stop", &dripline::service::stop, DL_BIND_CALL_GUARD_STREAMS )
            .def( "add_child", &dripline::service::add_child, DL_BIND_CALL_GUARD_STREAMS )
            .def( "add_async_child", &dripline::service::add_async_child, DL_BIND_CALL_GUARD_STREAMS )
            //.def( "noisy_func", []() { pybind11::scoped_ostream_redirect stream(std::cout, pybind11::module::import("sys").attr("stdout"));})

            .def( "on_request_message", &_service::on_request_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            ;
        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SERVICE */
