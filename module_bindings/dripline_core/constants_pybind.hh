#ifndef DRIPLINE_PYBIND_CONSTANTS
#define DRIPLINE_PYBIND_CONSTANTS

#include "dripline_constants.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{

    std::list< std::string > export_constants(pybind11::module& mod)
    {
        std::list< std::string > all_items;

        all_items.push_back("op_t");
        pybind11::enum_< dripline::op_t >( mod, "op_t", pybind11::arithmetic() )
                // the values
                .value( "set", dripline::op_t::set )
                .value( "get", dripline::op_t::get )
                .value( "cmd", dripline::op_t::cmd )
                .value( "unknown", dripline::op_t::unknown )
                // helpers for type conversion
                .def( "to_uint", (unsigned (*)(dripline::op_t))&dripline::to_int, "Convert an op_t to integer" )
                .def( "to_string", (std::string (*)(dripline::op_t))&dripline::to_string, "Convert an op_t to string" )
                .def_static( "to_op_t", (dripline::op_t (*)(unsigned))&dripline::to_op_t, "Convert an integer to op_t" )
                .def_static( "to_op_t", (dripline::op_t (*)(std::string))&dripline::to_op_t, "Convert an string to op_t" )
                ;

        all_items.push_back("msg_t");
        pybind11::enum_<dripline::msg_t>( mod, "msg_t", pybind11::arithmetic() )
                // the values
                .value( "reply", dripline::msg_t::reply )
                .value( "request", dripline::msg_t::request )
                .value( "alert", dripline::msg_t::alert )
                .value( "unknown", dripline::msg_t::unknown )
                // helpers for type conversion
                .def( "to_uint", (unsigned (*)(dripline::msg_t))&dripline::to_uint, "Convert a msg_t to integer" )
                .def( "to_string", (std::string (*)(dripline::msg_t))&dripline::to_string, "Convert a msg_t to string" )
                .def_static( "to_msg_t", (dripline::msg_t (*)(unsigned))&dripline::to_msg_t, "Convert an integer to msg_t" )
                .def_static( "to_msg_t", (dripline::msg_t (*)(std::string))&dripline::to_msg_t, "Convert a string to msg_t" )
                ;

        return all_items;
    } /* export_constants */
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_CONSTANTS */
