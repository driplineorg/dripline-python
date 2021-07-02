#ifndef DRIPLINE_PYBIND_SPECIFIER
#define DRIPLINE_PYBIND_SPECIFIER

#include "specifier.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    std::list< std::string > export_specifier( pybind11::module& mod )
    {
        std::list< std::string > all_items;
        all_items.push_back( "Specifier" );
        pybind11::class_< dripline::specifier, std::shared_ptr< dripline::specifier >
                        >( mod, "Specifier", "All routing key content after the first '.' delimiter" )
            .def( pybind11::init< const std::string& >(),
                  pybind11::arg( "unparsed" ) = "")
            .def( "parse", &dripline::specifier::parse, "parses the specifier and populates internal attributes", DL_BIND_CALL_GUARD_STREAMS )
            .def( "reparse", &dripline::specifier::reparse, "reparses and updates internal attributes", DL_BIND_CALL_GUARD_STREAMS )
            .def( "to_string", &dripline::specifier::to_string, "converts the routing key elements into a single, bindable, string" )
            ;
        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SPECIFIER */
