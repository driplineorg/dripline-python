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
        pybind11::class_< scarab::param >( mod, "Param" );
    }

} /* namespace scarab_pybind */
