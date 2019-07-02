/*
 * scarab_param_namespace_pybind.cc
 *
 * Created on: April 18, 2019
 *     Author: B.H. LaRoque
 */


#include "param_pybind.hh"
#include "param_value_pybind.hh"
#include "param_array_pybind.hh"
#include "param_node_pybind.hh"
#include "signal_handler_pybind.hh"

PYBIND11_MODULE( scarab, scarab_mod )
{
    // Param-related data objects
    scarab_pybind::export_param( scarab_mod );
    scarab_pybind::export_param_value( scarab_mod );
    scarab_pybind::export_param_array( scarab_mod );
    scarab_pybind::export_param_node( scarab_mod );
    // signal handler
    scarab_pybind::export_signal_handler( scarab_mod );
}
