#ifndef DRIPLINE_PYBIND_ENDPOINT
#define DRIPLINE_PYBIND_ENDPOINT

#include "pybind11/pybind11.h"
#include "pybind11/iostream.h"

#include "endpoint.hh"

#include "_endpoint_trampoline.hh"

namespace dripline_pybind
{

    std::list< std::string > export_endpoint( pybind11::module& mod )
    {
        std::list< std::string > all_items;

        all_items.push_back( "_Endpoint" );
        pybind11::class_< dripline::endpoint, _endpoint_trampoline, std::shared_ptr< dripline::endpoint > >( mod, "_Endpoint", "Endpoint binding" )
            .def( pybind11::init< const std::string& >(),
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect >() )

            // mv_ properties
            .def_property_readonly( "name", (std::string& (dripline::endpoint::*)()) &dripline::endpoint::name )
            .def_property_readonly( "service", ( dripline::service_ptr_t& (dripline::endpoint::*)()) &dripline::endpoint::service )


            // deal with messages
            .def( "submit_request_message", &dripline::endpoint::submit_request_message,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect,
                                        pybind11::gil_scoped_release >() )
            .def( "on_request_message", &dripline::endpoint::on_request_message,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect,
                                        pybind11::gil_scoped_release >() )
            .def( "on_reply_message", &dripline::endpoint::on_reply_message,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect,
                                        pybind11::gil_scoped_release >() )
            .def( "on_alert_message", &dripline::endpoint::on_alert_message,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect,
                                        pybind11::gil_scoped_release >() )
            .def( "do_get_request", &dripline::endpoint::do_get_request,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect,
                                        pybind11::gil_scoped_release >() )
            .def( "do_set_request", &dripline::endpoint::do_set_request,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect,
                                        pybind11::gil_scoped_release >() )
            .def( "do_cmd_request", &dripline::endpoint::do_cmd_request,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect,
                                        pybind11::gil_scoped_release >() )
            ;
            return all_items;
    }
} /* namespace dripline_pybind */
#endif /* DRIPLINE_PYBIND_ENDPOINT */
