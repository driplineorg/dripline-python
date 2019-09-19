#ifndef DRIPLINE_PYBIND_CORE_HH_
#define DRIPLINE_PYBIND_CORE_HH_

#include "core.hh"
#include "dripline_fwd.hh"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/iostream.h"

namespace dripline_pybind
{
    std::list< std::string>  export_core( pybind11::module& mod )
    {
        std::list< std::string > all_items;

        all_items.push_back( "SentMessagePackage" );
        pybind11::class_< dripline::sent_msg_pkg, std::shared_ptr< dripline::sent_msg_pkg > >( mod, "SentMessagePackage", "Data structure for sent messages" )
            ;

        all_items.push_back( "Core" );
        pybind11::class_< dripline::core,
                          /*core_trampoline,*/
                          std::shared_ptr< dripline::core >
                        >( mod, "Core", "lower-level class for AMQP message sending and receiving" )
            .def( pybind11::init< const scarab::param_node&,
                                  /*const std::string&, */
                                  const std::string&,
                                  const unsigned int,
                                  const std::string&,
                                  const bool
                                >(),
                   pybind11::call_guard< pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect >(),
                   pybind11::arg_v( "config", scarab::param_node(), "ParamNode()"),
                   /*pybind11::arg( "name" ) = "",*/
                   pybind11::arg( "broker" ) = "",
                   pybind11::arg( "port" ) = 0,
                   pybind11::arg( "auth_file" ) = "",
                   pybind11::arg( "make_connection" ) = true
            )

            //.def( "send", (dripline::sent_msg_pkg_ptr (_core::*)(dripline::request_ptr_t)) &_core::send, "send a request message" )
            .def( "send",
                    //(dripline::sent_msg_pkg_ptr (dripline::core::*)(dripline::request_ptr_t) const)&dripline::core::send,
                    //TODO: how do I gest a request_ptr_t from a msg_request?
                    [](dripline::core& a_core, dripline::msg_request& a_request){return a_core.send( dripline::request_ptr_t(std::copy(a_request)) );},
                    "send a request message" )
            //.def( "send", (dripline::sent_msg_pkg_ptr (dripline::core::*)(dripline::reply_ptr_t)) &dripline::core::send, "send a reply message" )
            //.def( "send", (dripline::sent_msg_pkg_ptr (dripline::core::*)(dripline::alert_ptr_t)) &dripline::core::send, "send an alert message" )

            /*
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
            */

            //.def
            ;
        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_CORE_HH_ */
