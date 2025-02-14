#ifndef DRIPLINE_PYBIND_SERVICE
#define DRIPLINE_PYBIND_SERVICE

#include "binding_helpers.hh"
#include "_service_trampoline.hh"

#include "core.hh"
#include "service.hh"

#include "authentication.hh"
#include "param_binding_helpers.hh"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/iostream.h"



namespace dripline_pybind
{
    std::list< std::string>  export_service( pybind11::module& mod )
    {
        std::list< std::string > all_items;
        all_items.push_back( "_Service" );
        pybind11::classh< _service,
                          _service_trampoline,
                          dripline::core,
                          dripline::endpoint,
                          dripline::receiver,
                          dripline::scheduler<>,
                          scarab::cancelable
                        >( mod, "_Service", "Service binding" )
            .def( pybind11::init< const scarab::param_node&,
                                  const scarab::authentication&,
                                  const bool
                                >(),
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg_v( "config", scarab::param_node(), "ParamNode()" ),
                  pybind11::arg_v( "auth", scarab::authentication(), "Authentication()" ),
                  pybind11::arg( "make_connection" ) = true
                )
            .def_property( "auth", (scarab::authentication& (dripline::service::*)()) &dripline::service::auth, 
                           [](_service& a_service, const scarab::authentication& a_auth){a_service.auth() = a_auth;}, 
                           pybind11::return_value_policy::reference_internal )
            .def_property( "enable_scheduling", &dripline::service::get_enable_scheduling, &dripline::service::set_enable_scheduling )
            .def_property_readonly( "alerts_exchange", (std::string& (dripline::service::*)()) &dripline::service::alerts_exchange )
            .def_property_readonly( "requests_exchange", (std::string& (dripline::service::*)()) &dripline::service::requests_exchange )
            .def_property_readonly( "sync_children", (std::map<std::string, dripline::endpoint_ptr_t>& (dripline::service::*)()) &dripline::service::sync_children )
            //TODO: need to deal with lr_ptr_t to bind this
            //.def_property_readonly( "async_children", &dripline::service::async_children )

            .def( "bind_keys",
                  &_service::bind_keys,
                  "overridable method to create all desired key bindings, overrides should still call this version",
                  DL_BIND_CALL_GUARD_STREAMS
                )
            .def( "bind_key",
                  // Note, need to take a service pointer so that we can accept derived types... I think
                  [](_service* an_obj, std::string&  an_exchange, std::string& a_key){return _service::bind_key(an_obj->channel(), an_exchange, an_obj->name(), a_key);},
                  pybind11::arg( "exchange" ),
                  pybind11::arg( "key" ),
                  "bind the service's message queue to a particular exchange and key",
                  DL_BIND_CALL_GUARD_STREAMS
            )
            
            .def( "run", &dripline::service::run, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            .def( "start", &dripline::service::start, DL_BIND_CALL_GUARD_STREAMS )
            .def( "listen", &dripline::service::listen, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            .def( "stop", &dripline::service::stop, DL_BIND_CALL_GUARD_STREAMS )
            .def( "add_child", &dripline::service::add_child, DL_BIND_CALL_GUARD_STREAMS )
            .def( "add_async_child", &dripline::service::add_async_child, DL_BIND_CALL_GUARD_STREAMS )
            //.def( "noisy_func", []() { pybind11::scoped_ostream_redirect stream(std::cout, pybind11::module::import("sys").attr("stdout"));})

            .def( "on_request_message", &_service::on_request_message, DL_BIND_CALL_GUARD_STREAMS_AND_GIL )
            ;
        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SERVICE */
