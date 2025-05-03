#ifndef DRIPLINE_PYBIND_ENDPOINT
#define DRIPLINE_PYBIND_ENDPOINT

#include "pybind11/pybind11.h"
#include "pybind11/iostream.h"

#include "binding_helpers.hh"
#include "endpoint.hh"

#include "_endpoint_trampoline.hh"

namespace dripline_pybind
{

    std::list< std::string > export_endpoint( pybind11::module& mod )
    {
        std::list< std::string > all_items;

        all_items.push_back( "_Endpoint" );
        pybind11::classh< dripline::endpoint,
                          _endpoint_trampoline 
                        >( mod, "_Endpoint", "Endpoint binding" )
            .def( pybind11::init< const std::string& >(), DL_BIND_CALL_GUARD_STREAMS )

            // mv_ properties
            .def_property_readonly( "name", (std::string& (dripline::endpoint::*)()) &dripline::endpoint::name )
            .def_property_readonly( "service", ( dripline::service& (dripline::endpoint::*)()) &dripline::endpoint::parent )


            // deal with messages
            .def( "submit_request_message", &dripline::endpoint::submit_request_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "directly submits a request message to the endpoint for processing" )
            .def( "on_request_message", &dripline::endpoint::on_request_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "callback to execute when a new request message is recieved, has a stanard implementation but available for override")
            .def( "on_reply_message", &dripline::endpoint::on_reply_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "callback to execute when a new reply message is recieved, has a stanard implementation but available for override")
            .def( "on_alert_message", &dripline::endpoint::on_alert_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "callback to execute when a new alert message is recieved" )
            .def( "do_get_request", &dripline::endpoint::do_get_request, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "overridable method for implementing get handling behavior" )
            .def( "do_set_request", &dripline::endpoint::do_set_request, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "overridable method for implementing set handling behavior" )
            .def( "do_cmd_request", &dripline::endpoint::do_cmd_request, DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "overridable method for implementing cmd handling behavior" )
            ;
            return all_items;
    }
} /* namespace dripline_pybind */
#endif /* DRIPLINE_PYBIND_ENDPOINT */
