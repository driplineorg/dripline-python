#ifndef DRIPLINE_PYBIND_CORE_HH_
#define DRIPLINE_PYBIND_CORE_HH_

#include "binding_helpers.hh"

#include "core.hh"
#include "dripline_fwd.hh"

#include "authentication.hh"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/iostream.h"

namespace dripline_pybind
{
    std::list< std::string>  export_core( pybind11::module& mod )
    {
        std::list< std::string > all_items;

        all_items.push_back( "SentMessagePackage" );
        pybind11::class_< dripline::sent_msg_pkg,
                          std::shared_ptr< dripline::sent_msg_pkg >
                        >( mod, "SentMessagePackage", "Data structure for sent messages" )
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
            // The bound functions use lambdas because the dripline::core functions include amqp_ptr_t arguments which aren't known to pybind11.
            //   Therefore when called from Python, the send process will use the default parameter, a new AMQP connection.
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
            ;

        // bind core's internal types
        pybind11::enum_<dripline::core::post_listen_status>(t_core, "PostListenStatus")
            .value("Unknown", dripline::core::post_listen_status::unknown)
            .value("MessageReceived", dripline::core::post_listen_status::message_received)
            .value("Timeout", dripline::core::post_listen_status::timeout)
            .value("SoftError", dripline::core::post_listen_status::soft_error)
            .value("HardError", dripline::core::post_listen_status::hard_error)
            ;

        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_CORE_HH_ */
