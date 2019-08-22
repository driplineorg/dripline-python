/*
 * KTPyNymph.cc
 *
 *  Created on: Feb 1, 2018
 *      Author: N. Oblath, L. Gladstone, B.H. LaRoque
 */

#include "param.hh"

#include "pybind11/pybind11.h"

namespace scarab_pybind
{

    void export_param_array( pybind11::module& mod )
    {
        // param_array
        pybind11::class_< scarab::param_array, scarab::param >( mod, "ParamArray" )
            .def( pybind11::init< >() )
            .def( "__str__", &scarab::param_array::to_string )
            .def( "__len__", &scarab::param_array::size,
                    "Returns the size of the array" )
            .def( "__getitem__", (scarab::param& (scarab::param_array::*)(unsigned)) &scarab::param_array::operator[],
                    pybind11::return_value_policy::reference_internal)
            .def( "__setitem__", [](scarab::param_array& an_obj, unsigned a_index, scarab::param& a_value){ an_obj.assign( a_index, a_value ); } )

            .def( "is_null", &scarab::param_array::is_null )
            .def( "is_array", &scarab::param_array::is_array )

            //TODO: has_subset()

            //TODO: remove size(), which is not part of the pythonic API
            .def( "size", &scarab::param_array::size,
                    "Returns the size of the array" )
            .def( "empty", &scarab::param_array::empty,
                    "True if the length is zero" )

            .def( "resize", &scarab::param_array::resize,
                    "Sets the size of the array; if smaller than the current size, the extra elements are deleted" )

            .def( "assign", (void (scarab::param_array::*)(unsigned, const scarab::param&)) &scarab::param_array::assign,
                    "Add a param object to the specified index in a array" )

            // Get value of the parameter, bringing along the default value
            .def( "get_value", (bool (scarab::param_array::*)(unsigned, bool) const) &scarab::param_array::get_value<bool>,
                    "Get parameter array value as a bool" )
            .def( "get_value", (unsigned (scarab::param_array::*)(unsigned, unsigned) const) &scarab::param_array::get_value<uint>,
                    "Get parameter array value as an unsigned integer" )
            .def( "get_value", (int (scarab::param_array::*)(unsigned, int) const) &scarab::param_array::get_value<int>,
                    "Get parameter array value as a signed integer" )
            .def( "get_value", (double (scarab::param_array::*)(unsigned, double) const) &scarab::param_array::get_value<double>,
                    "Get parameter array value as a float" )
            .def( "get_value", (std::string (scarab::param_array::*)(unsigned, const std::string& ) const) &scarab::param_array::get_value,
                    "Get parameter array value as a string" )

            .def( "push_back", (void (scarab::param_array::*)(const scarab::param&)) &scarab::param_array::push_back, "add a param object to the end of the array")
            //.def( "push_back", (void (scarab::param_array::*)(scarab::param&)) &scarab::param_array::push_back, "add a param object to the end of the array")
            .def( "push_front", (void (scarab::param_array::*)(const scarab::param&)) &scarab::param_array::push_front, "add a param object to the end of the array")
            //.def( "push_front", (void (scarab::param_array::*)(scarab::param&)) &scarab::param_array::push_front, "add a param object to the end of the array")

            .def( "append", &scarab::param_array::append )
            .def( "merge", &scarab::param_array::merge )
            .def( "erase", &scarab::param_array::erase )
            .def( "remove", &scarab::param_array::remove )
            .def( "clear", &scarab::param_array::clear )

            //TODO: iterators (see: https://github.com/pybind/pybind11/blob/master/tests/test_sequences_and_iterators.cpp)

            ;
    }

} /* namespace scarab_pybind */
