#ifndef DRIPLINE_PYBIND_SIMPLE_SERVICE
#define DRIPLINE_PYBIND_SIMPLE_SERVICE

#include "simple_service.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    std::list< std::string > export_run_simple_service( pybind11::module& mod )
    {
        std::list< std::string > all_items;
        all_items.push_back( "simple_service" );
        pybind11::class_< dripline::simple_service, std::shared_ptr< dripline::simple_service > >( mod, "simple_service", "Minimal example of a dripline service" )
            .def( pybind11::init< const scarab::param_node& >() )
            .def( "execute", &dripline::simple_service::execute )
            ;
        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SIMPLE_SERVICE */
