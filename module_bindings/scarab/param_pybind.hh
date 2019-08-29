/*
 * param_pybind.hh
 *
 *  Created on: Feb 1, 2018
 *      Author: N. Oblath, L. Gladstone, B.H. LaRoque
 */

#include "param.hh"

#include "pybind11/pybind11.h"
#include "pybind11/pytypes.h"

namespace scarab_pybind
{
    pybind11::object to_python( const scarab::param& a_param )
    {
    }

    void export_param( pybind11::module& mod )
    {
        // param
        pybind11::class_< scarab::param >( mod, "Param" )
            .def( pybind11::init< >() )
            .def( pybind11::init< scarab::param_value >() )

            .def( "__str__", &scarab::param::to_string )
            .def( "__call__", (scarab::param_value& (scarab::param::*)()) &scarab::param::operator(),
                    pybind11::return_value_policy::reference_internal )
            .def( "__getitem__", (scarab::param& (scarab::param::*)(unsigned)) &scarab::param::operator[],
                    pybind11::return_value_policy::reference_internal )
            .def( "__getitem__", (scarab::param& (scarab::param::*)(const std::string&)) &scarab::param::operator[],
                    pybind11::return_value_policy::reference_internal )
            //TODO: do we need __setitem__?

            .def( "is_null", &scarab::param::is_null )
            .def( "is_node", &scarab::param::is_node )
            .def( "is_array", &scarab::param::is_array )
            .def( "is_value", &scarab::param::is_value )

            .def( "as_array", (scarab::param_array& (scarab::param::*)()) &scarab::param::as_array,
                    pybind11::return_value_policy::reference_internal )
            .def( "as_node", (scarab::param_node& (scarab::param::*)()) &scarab::param::as_node,
                    pybind11::return_value_policy::reference_internal )
            .def( "as_value", (scarab::param_value& (scarab::param::*)()) &scarab::param::as_value,
                    pybind11::return_value_policy::reference_internal )

            .def( "to_python", [](const scarab::param& an_obj){ return pybind11::none(); } )

            //TODO: has_subset()

            //TODO: get_value() in its various types

            //TODO: merge()

            ;
    }

} /* namespace scarab_pybind */
