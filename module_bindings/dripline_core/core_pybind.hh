#ifndef DRIPLINE_PYBIND_CORE_HH_
#define DRIPLINE_PYBIND_CORE_HH_

#include "binding_helpers.hh"

#include "core.hh"
#include "dripline_fwd.hh"

#include "authentication.hh"

#include "rmqt_queue.h"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/iostream.h"

namespace dripline_pybind
{
    std::list< std::string>  export_core( pybind11::module& mod )
    {
        std::list< std::string > all_items;

        all_items.push_back( "QueueHandle" );
        pybind11::class_< BloombergLP::rmqt::QueueHandle >( mod, "QueueHandle",
            "Opaque handle to an AMQP queue. "
            "Returned by add_requests_*_queue() and add_alerts_*_queue(); "
            "passed to bind_requests_key(), bind_alerts_key(), and the queue property." )
            ;

        all_items.push_back( "SentMessagePackage" );
        pybind11::classh< dripline::sent_msg_pkg >( mod, "SentMessagePackage", "Data structure for sent messages" )
            .def_property_readonly( "successful_send", [](const dripline::sent_msg_pkg& an_obj){ return an_obj.f_successful_send; } )
            .def_property_readonly( "send_error_message", [](const dripline::sent_msg_pkg& an_obj){ return an_obj.f_send_error_message; } )
            ;

        all_items.push_back( "Core" );
        pybind11::classh< dripline::core
                        > t_core( mod, "Core", "lower-level class for AMQP message sending and receiving" );

        // bind the core class
        t_core            
            .def( pybind11::init< const scarab::param_node&,
                                  const scarab::authentication&,
                                  const bool
                                >(),
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg_v( "config", scarab::param_node(), "ParamNode()" ),
                  pybind11::arg_v( "auth", scarab::authentication(), "Authentication()" ),
                  pybind11::arg( "make_connection" ) = true
                )

            // Notes on send() bindings
            // The bound functions use lambdas to avoid exposing rmqcpp internal types to pybind11.
            // The bindings to these functions are not included in a trampoline class because we're not directly overriding the C++ send() functions.
            //   Therefore calls to send() from a base-class pointer will not redirect appropriately to the derived-class versions of send().
            .def( "send",
                  [](dripline::core& a_core, dripline::request_ptr_t a_request){return a_core.send(a_request);},
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "send a request message"
                )
            .def( "send",
                  [](dripline::core& a_core, dripline::reply_ptr_t a_reply){return a_core.send(a_reply);},
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "send a reply message"
                )
            .def( "send",
                  [](dripline::core& a_core, dripline::alert_ptr_t an_alert){return a_core.send(an_alert);},
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "send an alert message"
                )
            //.def_property( "address", std::static_cast< const std::string& (const dripline::core::*) >( &dripline::core::address ), [](dripline::core& a_core, const std::string& a_value){a_core.address() = a_value;} )
            .def_property( "address", [](const dripline::core& a_core){return a_core.address();}, [](dripline::core& a_core, const std::string& a_value){a_core.address() = a_value;} )
            .def_property( "port", &dripline::core::get_port, &dripline::core::set_port )
            .def_property( "username", [](const dripline::core& a_core){return a_core.username();}, [](dripline::core& a_core, const std::string& a_value){a_core.username() = a_value;} )
            .def_property( "password", [](const dripline::core& a_core){return a_core.password();}, [](dripline::core& a_core, const std::string& a_value){a_core.password() = a_value;} )
            .def_property( "requests_exchange", [](const dripline::core& a_core){return a_core.requests_exchange();}, [](dripline::core& a_core, const std::string& a_value){a_core.requests_exchange() = a_value;} )
            .def_property( "alerts_exchange", [](const dripline::core& a_core){return a_core.alerts_exchange();}, [](dripline::core& a_core, const std::string& a_value){a_core.alerts_exchange() = a_value;} )
            .def_property( "heartbeat_routing_key", [](const dripline::core& a_core){return a_core.heartbeat_routing_key();}, [](dripline::core& a_core, const std::string& a_value){a_core.heartbeat_routing_key() = a_value;} )
            .def_property( "max_payload_size", &dripline::core::get_max_payload_size, &dripline::core::set_max_payload_size )
            .def_property( "make_connection", &dripline::core::get_make_connection, &dripline::core::set_make_connection )
            .def_property( "max_connection_attempts", &dripline::core::get_max_connection_attempts, &dripline::core::set_max_connection_attempts )

            // Topology helpers (public in core)
            .def( "open_connection",
                  &dripline::core::open_connection,
                  DL_BIND_CALL_GUARD_STREAMS,
                  "Open the RabbitMQ connection and declare both exchanges in the topology. "
                  "Must be called before any add_*_queue() or bind_*_key() call." )
            .def( "add_requests_durable_queue",
                  &dripline::core::add_requests_durable_queue,
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg("queue_name"),
                  "Declare a durable queue on the requests exchange. "
                  "Must be called after open_connection(). "
                  "Returns a QueueHandle to pass to bind_requests_key()." )
            .def( "add_requests_ephemeral_queue",
                  &dripline::core::add_requests_ephemeral_queue,
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg("queue_name"),
                  "Declare an ephemeral (auto-delete) queue on the requests exchange. "
                  "Must be called after open_connection(). "
                  "Returns a QueueHandle to pass to bind_requests_key()." )
            .def( "add_alerts_durable_queue",
                  &dripline::core::add_alerts_durable_queue,
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg("queue_name"),
                  "Declare a durable queue on the alerts exchange. "
                  "Must be called after open_connection(). "
                  "Returns a QueueHandle to pass to bind_alerts_key()." )
            .def( "add_alerts_ephemeral_queue",
                  &dripline::core::add_alerts_ephemeral_queue,
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg("queue_name"),
                  "Declare an ephemeral (auto-delete) queue on the alerts exchange. "
                  "Must be called after open_connection(). "
                  "Returns a QueueHandle to pass to bind_alerts_key()." )
            .def( "bind_requests_key",
                  &dripline::core::bind_requests_key,
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg("queue_name"), pybind11::arg("routing_key"), pybind11::arg("queue"),
                  "Bind a queue to the requests exchange with the given routing key. "
                  "Must be called after add_requests_*_queue()." )
            .def( "bind_alerts_key",
                  &dripline::core::bind_alerts_key,
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg("queue_name"), pybind11::arg("routing_key"), pybind11::arg("queue"),
                  "Bind a queue to the alerts exchange with the given routing key. "
                  "Must be called after add_alerts_*_queue() (or add_requests_*_queue() "
                  "if sharing a single queue across both exchanges, as monitor does)." )
            ;

        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_CORE_HH_ */
