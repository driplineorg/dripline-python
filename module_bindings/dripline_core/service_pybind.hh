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
        // listener_receiver is only bound for Service binding
        // if we want more than this minimal binding it should go
        // into its own header
        pybind11::class_< dripline::listener_receiver, std::shared_ptr< dripline::listener_receiver> >(mod, "__ListenerReceiver" );

        std::list< std::string > all_items;
        all_items.push_back( "Service" );
        pybind11::class_< dripline::service, scarab::cancelable, dripline::listener_receiver, std::shared_ptr< dripline::service > >( mod, "Service", "responsible for dripline-compliant AMQP message sending and receiving" )
            .def( pybind11::init< const scarab::param_node&,
                                  const std::string&,
                                  const std::string&,
                                  const unsigned int,
                                  const std::string&,
                                  const bool
                                >(),
                   pybind11::call_guard< pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect >(),
                   pybind11::arg( "config" ) = scarab::param_node(),
                   pybind11::arg( "name" ) = "",
                   pybind11::arg( "broker" ) = "",
                   pybind11::arg( "port" ) = 0,
                   pybind11::arg( "auth_file" ) = "",
                   pybind11::arg( "make_connection" ) = true
            )

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
