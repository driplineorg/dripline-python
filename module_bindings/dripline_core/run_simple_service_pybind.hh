#ifndef DRIPLINE_PYBIND_SIMPLE_SERVICE
#define DRIPLINE_PYBIND_SIMPLE_SERVICE

#include "binding_helpers.hh"

#include "simple_service.hh"

#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    std::list< std::string > export_run_simple_service( pybind11::module& mod )
    {
        std::list< std::string > all_items;
        all_items.push_back( "simple_service" );
        pybind11::classh< dripline::simple_service >( mod, "simple_service", "Minimal example of a dripline service" )
            .def( pybind11::init< const scarab::param_node& >() )
            .def( "execute", &dripline::simple_service::execute, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            ;
        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SIMPLE_SERVICE */
