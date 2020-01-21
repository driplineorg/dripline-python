#ifndef DRIPLINE_PYBIND_CORE_HH_
#define DRIPLINE_PYBIND_CORE_HH_

#include "binding_helpers.hh"

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
        pybind11::class_< dripline::sent_msg_pkg,
                          std::shared_ptr< dripline::sent_msg_pkg >
                        >( mod, "SentMessagePackage", "Data structure for sent messages" )
            ;

        all_items.push_back( "Core" );
        pybind11::class_< dripline::core,
                          std::shared_ptr< dripline::core >
                        >( mod, "Core", "lower-level class for AMQP message sending and receiving" )
            .def( pybind11::init< const scarab::param_node&,
                                  const std::string&,
                                  const unsigned int,
                                  const std::string&,
                                  const bool
                                >(),
                   DL_BIND_CALL_GUARD_STREAMS,
                   pybind11::arg_v( "config", scarab::param_node(), "ParamNode()"),
                   pybind11::arg( "broker" ) = "",
                   pybind11::arg( "port" ) = 0,
                   pybind11::arg( "auth_file" ) = "",
                   pybind11::arg( "make_connection" ) = true
                )

            .def( "send",
                  [](dripline::core& a_core, dripline::request_ptr_t a_request){return a_core.send(a_request);},
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "send a request message"
                )
            .def( "send",
                  [](dripline::core& a_core, dripline::reply_ptr_t a_reply){return a_core.send(a_reply);},
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "send a reply message"
                )
            .def( "send",
                  [](dripline::core& a_core, dripline::alert_ptr_t an_alert){return a_core.send(an_alert);},
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL,
                  "send an alert message"
                )

            ;
        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_CORE_HH_ */
