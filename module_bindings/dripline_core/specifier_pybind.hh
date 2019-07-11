#include "specifier.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    void export_specifier( pybind11::module& mod )
    {
        pybind11::class_< dripline::specifier, std::shared_ptr< dripline::specifier > >
            ( mod, "specifier", "All data after the first '.' character" )
            .def( pybind11::init< const std::string& >() )
            .def( "parse", &dripline::specifier::parse )
            .def( "reparse", &dripline::specifier::reparse )
            .def( "to_string", &dripline::specifier::to_string );

    } //end export_specifier
} //end dripline_pybind namespace
