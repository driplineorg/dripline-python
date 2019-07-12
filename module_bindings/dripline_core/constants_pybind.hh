#include "dripline_constants.hh"

#include "pybind11/pybind11.h"

namespace dripline_pybind
{

    void export_constants(pybind11::module& mod)
    {

        pybind11::enum_< dripline::op_t >( mod, "op_t", pybind11::arithmetic() )
                // the values
                .value( "set", dripline::op_t::set )
                .value( "get", dripline::op_t::get )
                .value( "config", dripline::op_t::config ) // deprecated as of v2.0.0 (dripline_cpp)
                .value( "send", dripline::op_t::send )
                .value( "run", dripline::op_t::run )
                .value( "cmd", dripline::op_t::cmd )
                .value( "unknown", dripline::op_t::unknown )
                // helpers for type conversion
                .def( "to_uint", (uint32_t (*)(dripline::op_t))&dripline::to_uint, "Convert an op_t to int" )
                .def( "to_string", (std::string (*)(dripline::op_t))&dripline::to_string, "Convert an op_t to string" )
                .def_static( "to_op_t", (dripline::op_t (*)(uint32_t))&dripline::to_op_t, "Convert an uint to op_t" )
                .def_static( "to_op_t", (dripline::op_t (*)(std::string))&dripline::to_op_t, "Convert an string to op_t" )
                ;

        pybind11::enum_<dripline::msg_t>( mod, "msg_t", pybind11::arithmetic() )
                // the values
                .value( "reply", dripline::msg_t::reply )
                .value( "request", dripline::msg_t::request )
                .value( "alert", dripline::msg_t::alert )
                .value( "unknown", dripline::msg_t::unknown )
                // helpers for type conversion
                .def( "to_uint", (uint32_t (*)(dripline::msg_t))&dripline::to_uint, "Convert a msg_t to int" )
                .def( "to_string", (std::string (*)(dripline::msg_t))&dripline::to_string, "Convert a msg_t to string" )
                .def_static( "to_msg_t", (dripline::msg_t (*)(uint32_t))&dripline::to_msg_t, "Convert an uint to msg_t" )
                .def_static( "to_msg_t", (dripline::msg_t (*)(std::string))&dripline::to_msg_t, "Convert a string to msg_t" )
                ;

    }

}
/* namespace dripline_pybind */
