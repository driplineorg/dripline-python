#include "dripline_constants.hh"

#include "pybind11/pybind11.h"

namespace dripline_cpp_pybind
{

    void ExportDriplineCppConstantsPybind( pybind11::module& mod )
    {
       
        pybind11::enum_<dripline::op_t>(mod, "op_t", pybind11::arithmetic())
            .value("set", dripline::op_t::set)
            .value("get", dripline::op_t::get)
            .value("config", dripline::op_t::config) // deprecated as of v2.0.0 (dripline_cpp)
            .value("send", dripline::op_t::send)
            .value("run", dripline::op_t::run)
            .value("cmd", dripline::op_t::cmd)
            .value("unknown", dripline::op_t::unknown)
            .export_values();
 
        mod.def("to_uint", pybind11::overload_cast<dripline::op_t>(&dripline::to_uint), "Convert an op_t to int");
        mod.def("to_op_t", pybind11::overload_cast<uint_32>(&dripline::to_op_t), "Convert an uint to op_t");
        // originally operator <<
        mod.def("op_t_ostream", [](std::ostream& a_os, dripline::op_t an_op) { a_os << an_op; });
        mod.def("to_string", pybind11::overload_cast<dripline::op_t>(&dripline::to_string), "Convert an op_t to string");
        mod.def("to_op_t", pybind11::overload_cast<std::string>(&dripline::to_op_t), "Convert an string to op_t");

        pybind11::enum_<dripline::msg_t>(mod, "msg_t", pybind11::arithmetic())
            .value("reply", dripline::msg_t::reply)
            .value("request", dripline::msg_t::request)
            .value("alert", dripline::msg_t::alert)
            .value("unknown", dripline::msg_t::unknown)
            .export_values();

        mod.def("to_uint", pybind11::overload_cast<dripline::msg_t>(&dripline::to_uint), "Convert a msg_t to int");
        mod.def("to_msg_t", pybind11::overload_cast<uint_32>(&dripline::to_smg_t), "Convert an uint to msg_t");
        // originally operator <<
        mod.def("msg_t_ostream", [](std::ostream& a_os, dripline::msg_t a_msg) { a_os << a_msg; });

    }
    
} /* namespace dripline_cpp_pybind */
