#ifndef DRIPLINE_PYBIND_ENDPOINT
#define DRIPLINE_PYBIND_ENDPOINT

#include "endpoint.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    void export_endpoint( pybind11::module& mod )
    {
	pybind11::class_< dripline::endpoint, endpoint_trampoline >( mod, "_Endpoint", "Endpoint binding" )
	    .def( pybind11::init< const std::string& >() )
	    .def( "submit_request_message", &dripline::endpoint::submit_request_message )
	    .def( "do_get_request", &dripline::endpoint::do_get_request )
	    .def( "do_set_request", &dripline::endpoint::do_set_request )
	    .def( "do_cmd_request", &dripline::endpoint::do_cmd_request );
	
    } //end export_endpoint
} //end dripline_pybind namespace

#endif /* DRIPLINE_PYBIND_ENDPOINT */
