#ifndef DRIPLINE_PYBIND_SPECIFIER
#define DRIPLINE_PYBIND_SPECIFIER

#include "specifier.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    void export_specifier( pybind11::module& mod )
    {
        pybind11::class_< dripline::specifier, std::shared_ptr< dripline::specifier > >( mod, "specifier",
                "All routing key content after the first '.' delimiter" )
            .def( pybind11::init< const std::string& >() )
            .def( "parse", &dripline::specifier::parse )
            .def( "reparse", &dripline::specifier::reparse )
            .def( "to_string", &dripline::specifier::to_string )
            ;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SPECIFIER */
