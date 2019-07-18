#ifndef DRIPLINE_PYBIND_SERVICE
#define DRIPLINE_PYBIND_SERVICE

#include "service.hh"
#include "pybind11/pybind11.h"
#include "pybind11/iostream.h"
#include "../scarab/param_node_pybind.hh"

namespace dripline_pybind
{
    void export_service( pybind11::module& mod )
    {
        pybind11::class_< dripline::service, std::shared_ptr< dripline::service > >( mod, "Service", "Used to send and receive simple messages" )
            
             .def( pybind11::init< pybind11::arg("a_config") = const scarab_pybind::ParamNode(), pybind11::arg("a_queue_name") = const "", pybind11::arg("a_broker_address") = const "", pybind11::arg("a_port") = const 0, pybind11::arg("a_auth_file") = const "", pybind11::arg("a_make_connection") = const 1 >() )
            
            /* ORIGINAL INIT<> FUNCTION */
            /*  .def( pybind11::init< const scarab::param_node&, const std::string&, const std::string&, const unsigned int, const std::string&, const bool >() ) */
                .def( "start", &dripline::service::start )
                .def( "listen", &dripline::service::listen )
                .def( "stop", &dripline::service::stop )
                .def( "add_child", &dripline::service::add_child )
                .def( "add_async_child", &dripline::service::add_async_child )
                .def( "noisy_func", []() { pybind11::scoped_ostream_redirect stream(std::cout, pybind11::module::import("sys").attr("stdout"));});
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SERVICE */
