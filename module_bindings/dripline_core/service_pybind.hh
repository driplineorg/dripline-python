#ifndef DRIPLINE_PYBIND_SERVICE
#define DRIPLINE_PYBIND_SERVICE

#include "service.hh"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/iostream.h"

namespace dripline_pybind
{
    std::list< std::string>  export_service( pybind11::module& mod )
    {
        std::list< std::string > all_items;
        all_items.push_back( "Service" );
        pybind11::class_< dripline::service,
                          dripline::scheduler<>,
                          scarab::cancelable,
                          std::shared_ptr< dripline::service >
                        >( mod, "Service", "responsible for dripline-compliant AMQP message sending and receiving" )
            .def( pybind11::init< const scarab::param_node&,
                                  const std::string&,
                                  const std::string&,
                                  const unsigned int,
                                  const std::string&,
                                  const bool
                                >(),
                   pybind11::call_guard< pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect >(),
                   pybind11::arg_v( "config", scarab::param_node(), "ParamNode()"),
                   pybind11::arg( "name" ) = "",
                   pybind11::arg( "broker" ) = "",
                   pybind11::arg( "port" ) = 0,
                   pybind11::arg( "auth_file" ) = "",
                   pybind11::arg( "make_connection" ) = true
            )

            .def_property( "enable_scheduling", &dripline::service::get_enable_scheduling, &dripline::service::set_enable_scheduling )

            .def( "start", &dripline::service::start,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect,
                                        pybind11::gil_scoped_release >() )
            .def( "listen", &dripline::service::listen,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect,
                                        pybind11::gil_scoped_release >() )
            .def( "stop", &dripline::service::stop,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect >() )
            .def( "add_child", &dripline::service::add_child,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect >() )
            .def( "add_async_child", &dripline::service::add_async_child,
                  pybind11::call_guard< pybind11::scoped_ostream_redirect,
                                        pybind11::scoped_estream_redirect >() )
            .def( "noisy_func", []() { pybind11::scoped_ostream_redirect stream(std::cout, pybind11::module::import("sys").attr("stdout"));})
            ;
        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SERVICE */
