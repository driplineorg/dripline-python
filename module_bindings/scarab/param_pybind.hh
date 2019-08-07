/*
 * param_pybind.hh
 *
 *  Created on: Feb 1, 2018
 *      Author: N. Oblath, L. Gladstone, B.H. LaRoque
 */

#include "param.hh"

#include "pybind11/pybind11.h"

namespace scarab_pybind
{

    void export_param( pybind11::module& mod )
    {
        // param
        pybind11::class_< scarab::param >( mod, "Param" )

            .def( "__str__", &scarab::param::to_string )

            .def( "is_null", &scarab::param::is_null )
            .def( "is_node", &scarab::param::is_node )
            .def( "is_array", &scarab::param::is_array )
            .def( "is_value", &scarab::param::is_value )

            ;
    }

} /* namespace scarab_pybind */
