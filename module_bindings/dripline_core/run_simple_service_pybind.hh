#include "simple_service.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    void export_run_simple_service( pybind11::module& mod )
    {
        pybind11::class_< dripline::simple_service, std::shared_ptr< dripline::simple_service > >( mod, "simple_service", "Minimal example of a dripline service" )
                .def( pybind11::init< const scarab::param_node& >() )
                .def( "execute", &dripline::simple_service::execute );

    } //end export_simple_service
} //end dripline_pybind namespace
