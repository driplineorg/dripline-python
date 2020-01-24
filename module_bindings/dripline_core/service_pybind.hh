#ifndef DRIPLINE_PYBIND_SERVICE
#define DRIPLINE_PYBIND_SERVICE

#include "binding_helpers.hh"
#include "service_trampoline.hh"

#include "core.hh"
#include "service.hh"

#include "param_binding_helpers.hh"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/iostream.h"


namespace dripline_pybind
{
    std::list< std::string>  export_service( pybind11::module& mod )
    {
        std::list< std::string > all_items;
        all_items.push_back( "Service" );
        pybind11::class_< _service,
                          _service_trampoline,
                          dripline::core,
                          dripline::endpoint,
                          dripline::scheduler<>,
                          scarab::cancelable,
                          std::shared_ptr< _service >
                        >( mod, "Service", "responsible for dripline-compliant AMQP message sending and receiving" )
            .def( pybind11::init< const scarab::param_node&,
                                  const std::string&,
                                  const std::string&,
                                  const unsigned int,
                                  const std::string&,
                                  const bool
                                >(),
                   DL_BIND_CALL_GUARD_STREAMS,
                   pybind11::arg_v( "config", scarab::param_node(), "ParamNode()"),
                   pybind11::arg( "name" ) = "",
                   pybind11::arg( "broker" ) = "",
                   pybind11::arg( "port" ) = 0,
                   pybind11::arg( "auth_file" ) = "",
                   pybind11::arg( "make_connection" ) = true
            )
            .def( pybind11::init( []( const pybind11::dict a_config,
                                      const std::string& a_name,
                                      const std::string& a_broker,
                                      const unsigned int a_port,
                                      const std::string& a_auth_file,
                                      const bool a_make_connection )
                                  { return new  _service( (scarab_pybind::to_param(a_config))->as_node(),
                                                          a_name,
                                                          a_broker,
                                                          a_port,
                                                          a_auth_file,
                                                          a_make_connection); } ),
                   DL_BIND_CALL_GUARD_STREAMS,
                   pybind11::arg( "config"),
                   pybind11::arg( "name" ) = "",
                   pybind11::arg( "broker" ) = "",
                   pybind11::arg( "port" ) = 0,
                   pybind11::arg( "auth_file" ) = "",
                   pybind11::arg( "make_connection" ) = true
            )

            // mv_ bindings
            .def_property( "enable_scheduling", &dripline::service::get_enable_scheduling, &dripline::service::set_enable_scheduling )
            .def_property_readonly( "alerts_exchange", (std::string& (dripline::service::*)()) &dripline::service::alerts_exchange )
            .def_property_readonly( "requests_exchange", (std::string& (dripline::service::*)()) &dripline::service::requests_exchange )

            .def( "bind_keys", 
                  &_service::bind_keys, 
                  "overridable method to create all desired key bindings, overrides should still call this version",
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL
                )
            .def( "bind_key",
                  // Note, need to take a service pointer so that we can accept derived types... I think
                  [](_service* an_obj, std::string&  an_exchange, std::string& a_key){return _service::bind_key(an_obj->channel(), an_exchange, an_obj->name(), a_key);},
                  pybind11::arg( "exchange" ),
                  pybind11::arg( "key" ),
                  "bind the service's message queue to a particular exchange and key",
                  DL_BIND_CALL_GUARD_STREAMS
            )
            .def( "start", &dripline::service::start, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            .def( "listen", &dripline::service::listen, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            .def( "stop", &dripline::service::stop, DL_BIND_CALL_GUARD_STREAMS )
            .def( "add_child", &dripline::service::add_child, DL_BIND_CALL_GUARD_STREAMS )
            .def( "add_async_child", &dripline::service::add_async_child, DL_BIND_CALL_GUARD_STREAMS )
            //.def( "noisy_func", []() { pybind11::scoped_ostream_redirect stream(std::cout, pybind11::module::import("sys").attr("stdout"));})

            .def( "on_alert_message", &_service::on_alert_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            ;
        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SERVICE */
