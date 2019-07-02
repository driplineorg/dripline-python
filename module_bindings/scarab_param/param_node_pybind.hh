/*
 *  Created on: Feb 1, 2018
 *      Author: N. Oblath, L. Gladstone, B.H. LaRoque
 */

#include "param.hh"

#include "pybind11/pybind11.h"

namespace scarab_pybind
{

    void export_param_node(pybind11::module& mod)
    {
        // param_node
        pybind11::class_< scarab::param_node, scarab::param >(mod, "ParamNode").def(pybind11::init< >())

        .def("add", (bool (scarab::param_node::*)(const std::string&, const scarab::param&)) &scarab::param_node::add, "Add a param object to a node")

        .def( "at", (scarab::param& (scarab::param_node::*)(const std::string&)) &scarab::param_node::operator[], "Get the param object for a given key" )

        // Get value of the parameter, bringing along the default value
        .def( "get_value", (bool (scarab::param_node::*)(const std::string&, bool) const) &scarab::param_node::get_value<bool>,
        "Get parameter node value as a bool" )
        .def( "get_value", (unsigned (scarab::param_node::*)(const std::string&, unsigned) const) &scarab::param_node::get_value<uint>,
        "Get parameter node value as an unsigned integer" )
        .def( "get_value", (int (scarab::param_node::*)(const std::string&, int) const) &scarab::param_node::get_value<int>,
        "Get parameter node value as a signed integer" )
        .def( "get_value", (double (scarab::param_node::*)(const std::string&, double) const) &scarab::param_node::get_value<double>,
        "Get parameter node value as a float" )
        .def( "get_value", (std::string (scarab::param_node::*)(const std::string&, const std::string& ) const) &scarab::param_node::get_value,
        "Get parameter node value as a string" )
        ;
    }
}
/* namespace Nymph */
