#ifndef DRIPLINE_PYBIND_SERVICE
#define DRIPLINE_PYBIND_SERVICE

#include "binding_helpers.hh"
#include "_service_trampoline.hh"

#include "core.hh"
#include "message_dispatcher.hh"
#include "service.hh"

#include "rmqt_queue.h"

#include "authentication.hh"
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
        pybind11::classh< _service,
                          _service_trampoline,
                          dripline::core,
                          dripline::endpoint,
                          dripline::message_dispatcher,
                          dripline::receiver,
                          dripline::scheduler<>,
                          scarab::cancelable
                        >( mod, "_Service", "Service binding" )
            .def( pybind11::init< const scarab::param_node&,
                                  const scarab::authentication&,
                                  const bool
                                >(),
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg_v( "config", scarab::param_node(), "ParamNode()" ),
                  pybind11::arg_v( "auth", scarab::authentication(), "Authentication()" ),
                  pybind11::arg( "make_connection" ) = true
                )
            .def_property( "auth", (scarab::authentication& (dripline::service::*)()) &dripline::service::auth, 
                           [](_service& a_service, const scarab::authentication& a_auth){a_service.auth() = a_auth;}, 
                           pybind11::return_value_policy::reference_internal )

            // Notes on send() bindings
            // The Service.send() functions are useful because they set the sender service name in the message before sending.
            // The bound functions use lambdas to avoid exposing rmqcpp internal types to pybind11.
            // The bindings to these functions are not included in the trampoline class because we're not directly overriding the C++ send() functions.
            .def( "send",
                  [](_service& a_service, dripline::request_ptr_t a_request){return a_service.send(a_request);},
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "send a request message"
                )
            .def( "send",
                  [](_service& a_service, dripline::reply_ptr_t a_reply){return a_service.send(a_reply);},
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "send a reply message"
                )
            .def( "send",
                  [](_service& a_service, dripline::alert_ptr_t an_alert){return a_service.send(an_alert);},
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "send an alert message"
                )
          
            .def_property( "enable_scheduling", &dripline::service::get_enable_scheduling, &dripline::service::set_enable_scheduling )
            .def_property_readonly( "sync_children", (std::map<std::string, dripline::endpoint_ptr_t>& (dripline::service::*)()) &dripline::service::sync_children )
            //TODO: need to deal with lr_ptr_t to bind this
            //.def_property_readonly( "async_children", &dripline::service::async_children )

            .def( "run", &dripline::service::run, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            .def( "start", &dripline::service::start, DL_BIND_CALL_GUARD_STREAMS )
            .def( "listen", &dripline::service::listen, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            .def( "stop", &dripline::service::stop, DL_BIND_CALL_GUARD_STREAMS )
            .def( "add_child", &dripline::service::add_child, DL_BIND_CALL_GUARD_STREAMS )
            .def( "add_async_child", &dripline::service::add_async_child, DL_BIND_CALL_GUARD_STREAMS )
            //.def( "noisy_func", []() { pybind11::scoped_ostream_redirect stream(std::cout, pybind11::module::import("sys").attr("stdout"));})

            .def( "on_request_message", &_service::on_request_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )

            // Message handler overrides
            .def( "on_reply_message", &_service::on_reply_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "callback to execute when a new reply message is received; available for override" )
            .def( "on_alert_message", &_service::on_alert_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "callback to execute when a new alert message is received; available for override" )

            // Request handler overrides
            .def( "do_run_request", &_service::do_run_request, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "overridable method for implementing run handling behavior" )
            .def( "do_get_request", &_service::do_get_request, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "overridable method for implementing get handling behavior" )
            .def( "do_set_request", &_service::do_set_request, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "overridable method for implementing set handling behavior" )
            .def( "do_cmd_request", &_service::do_cmd_request, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "overridable method for implementing cmd handling behavior" )

            // Service lifecycle hook overrides (called by start() in order)
            .def( "open_channels", &_service::open_channels, DL_BIND_CALL_GUARD_STREAMS,
                  "virtual hook: open the AMQP connection; called first by start()" )
            .def( "add_queues", &_service::add_queues, DL_BIND_CALL_GUARD_STREAMS,
                  "virtual hook: declare AMQP queues in the topology; called second by start()" )
            .def( "bind_keys", &_service::bind_keys, DL_BIND_CALL_GUARD_STREAMS,
                  "virtual hook: bind routing keys to queues; called third by start()" )
            .def( "start_threads", &_service::start_threads, DL_BIND_CALL_GUARD_STREAMS,
                  "virtual hook: start heartbeat and scheduler threads; called fourth by start()" )
            .def( "stop_threads", &_service::stop_threads, DL_BIND_CALL_GUARD_STREAMS,
                  "virtual hook: join heartbeat and scheduler threads; called by listen() and stop()" )

            // Message dispatcher override
            .def( "submit_message", &_service::submit_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "virtual hook: dispatch an assembled Dripline message; called by the rmqcpp callback thread" )

            // Note: the "queue" property is inherited from the MessageDispatcher base class
            //       (registered in message_dispatcher_pybind.hh)
            ;

        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SERVICE */
