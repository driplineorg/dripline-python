#ifndef DRIPLINE_PYBIND_ENDPOINT
#define DRIPLINE_PYBIND_ENDPOINT

#include "endpoint.hh"
#include "pybind11/pybind11.h"
#include "endpoint_trampoline.hh"

namespace dripline_pybind
{
    class _endpoint : public dripline::endpoint
    {
        public:
            using dripline::endpoint::do_get_request;
            using dripline::endpoint::do_set_request;
            using dripline::endpoint::do_cmd_request;
    };

    void export_endpoint( pybind11::module& mod )
    {
        pybind11::class_< dripline::endpoint, endpoint_trampoline, std::shared_ptr< dripline::endpoint > >( mod, "_Endpoint", "Endpoint binding" )
                .def( pybind11::init< const std::string& >() )
                .def( "submit_request_message", &dripline::endpoint::submit_request_message )
                .def( "do_get_request", &_endpoint::do_get_request )
                .def( "do_set_request", &_endpoint::do_set_request )
                .def( "do_cmd_request", &_endpoint::do_cmd_request )
                .def( "test_function", &_endpoint::test_function )
                .def_property("name", (std::string& (dripline::endpoint::*)()) &dripline::endpoint::name,
                              [](dripline::endpoint& an_obj, const std::string& a_name ){ an_obj.name() = a_name; } )
            //.def( "get_name", (std::string& (dripline::endpoint::*)()) &dripline::endpoint::name,
            //          "Get name of an endpoint as a string" )
                ;
                mod.def( "do_test_function", &dripline::do_test_function );
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_ENDPOINT */
