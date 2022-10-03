#ifndef DRIPLINE_PYBIND_MESSAGE
#define DRIPLINE_PYBIND_MESSAGE

#include "binding_helpers.hh"

#include "message.hh"
#include "message_trampoline.hh"

#include "pybind11/pybind11.h"
#include "pybind11/iostream.h"

#include "uuid.hh"

#include "logger.hh"
LOGGER( dlog_mph, "message_pybind.hh" )

namespace dripline_pybind
{

    std::list< std::string >  export_message( pybind11::module& mod )
    {
        std::list< std::string > all_items;

        /********
         message
         ********/
        all_items.push_back( "Message" );
        pybind11::class_< dripline::message, message_trampoline, std::shared_ptr< dripline::message > > message( mod, "Message", "base class for all dripline messages" );

        // internal types
        pybind11::enum_< dripline::message::encoding >( message, "encoding", "mime-type of message encoding" )
            .value( "json", dripline::message::encoding::json )
            ;

        // the message class itself
        message
            // constructor(s)
            .def( pybind11::init< >() )

            // properties
            // mv_referrable
            .def_property( "routing_key", (std::string& (dripline::message::*)()) &dripline::message::routing_key,
                           [](dripline::message& an_obj, const std::string& a_routing_key ){ an_obj.routing_key() = a_routing_key; } )
            .def_property( "correlation_id", (std::string& (dripline::message::*)()) &dripline::message::correlation_id,
                           [](dripline::message& an_obj, const std::string& a_correlation_id ){ an_obj.correlation_id() = a_correlation_id; } )
            .def_property( "reply_to", (std::string& (dripline::message::*)()) &dripline::message::reply_to,
                           [](dripline::message& an_obj, const std::string& a_reply_to ){ an_obj.reply_to() = a_reply_to; } )
            .def_property( "timestamp", (std::string& (dripline::message::*)()) &dripline::message::timestamp,
                           [](dripline::message& an_obj, const std::string& a_timestamp ){ an_obj.timestamp() = a_timestamp; } )
            // mv_accessible
            .def_property( "encoding", &dripline::message::get_encoding, &dripline::message::set_encoding )
            // non mv_* properties
            .def_property( "specifier",
                           (dripline::specifier& (dripline::message::*)())&dripline::message::parsed_specifier,
                           [](dripline::message& an_obj, const dripline::specifier& a_specifier ){ an_obj.parsed_specifier() = a_specifier; },
                           pybind11::return_value_policy::reference_internal
                         )
            .def_property_readonly( "message_type", &dripline::message::message_type )
            .def_property( "sender_info", &dripline::message::get_sender_info, &dripline::message::set_sender_info )
            .def_property( "payload",
                           (scarab::param& (dripline::message::*)())&dripline::message::payload,
                           [](dripline::message& an_obj, scarab::param& a_payload){ an_obj.set_payload(a_payload.clone()); },
                           pybind11::return_value_policy::reference_internal
                         )

            // methods to check message type
            .def( "is_request", &dripline::message::is_request, "Returns true if the message is a request, false otherwise" )
            .def( "is_reply", &dripline::message::is_reply, "Returns true if the message is a reply, false otherwise" )
            .def( "is_alert", &dripline::message::is_alert, "Returns true if the message is an alert, false otherwise" )


            .def( "encode_full_message", [](const dripline::message& a_message){ return a_message.encode_full_message(4000); }, DL_BIND_CALL_GUARD_STREAMS )
            ;

        /************
         msg_request
         ************/
        all_items.push_back( "MsgRequest" );
        pybind11::class_< dripline::msg_request, msg_request_trampoline, std::shared_ptr< dripline::msg_request >
                        >( mod, "MsgRequest", message, "dripline messages containing a request to be sent to an endpoint" )
            // constructor(s)
            .def( pybind11::init< >() )

            // conversion to string
            .def( "__str__", [](dripline::request_ptr_t a_req){
              scarab::param_node t_encoding_options;
              t_encoding_options.add( "style", "pretty" );
              return a_req->encode_full_message(5000, t_encoding_options);
            } )

            // properties
            // mv_referrable
            //TODO even better if we could interface with python's UUID library instead of passing strings
            .def_property( "lockout_key",
                           [](dripline::request_ptr_t a_req){ return boost::uuids::to_string(a_req->lockout_key()); },
                           [](dripline::request_ptr_t a_req, const std::string& a_lockout_key ){
                                bool t_lockout_key_valid = true;
                                a_req->lockout_key() = dripline::uuid_from_string( a_lockout_key, t_lockout_key_valid );
                                a_req->set_lockout_key_valid( t_lockout_key_valid );
                             }
                         )
            // mv_accessible
            .def_property( "lockout_key_valid", &dripline::msg_request::get_lockout_key_valid, &dripline::msg_request::set_lockout_key_valid )
            .def_property( "message_operation", &dripline::msg_request::get_message_operation, &dripline::msg_request::set_message_operation )

            // general methods
            .def_static( "create",
                         [](scarab::param& a_payload,
                            dripline::op_t a_msg_op,
                            std::string& a_routing_key,
                            std::string& a_specifier,
                            std::string& a_reply_to,
                            dripline::message::encoding an_encoding)
                           {return dripline::msg_request::create( a_payload.clone(), a_msg_op, a_routing_key, a_specifier, a_reply_to, an_encoding);},
                         pybind11::arg( "payload" ) = scarab::param(),
                         pybind11::arg( "msg_op" ) = dripline::op_t::unknown,
                         pybind11::arg( "routing_key" ) = "",
                         pybind11::arg( "specifier" ) = "",
                         pybind11::arg( "reply_to" ) = "",
                         pybind11::arg( "encoding" ) = dripline::message::encoding::json,
                         "create and populate a new MsgRequest instance",
                         DL_BIND_CALL_GUARD_STREAMS
                       )
            .def( "reply",
                  [](dripline::request_ptr_t a_req,
                     const unsigned a_return_code,
                     const std::string& a_return_message,
                     scarab::param& a_payload)
                    {return a_req->reply( a_return_code, a_return_message, a_payload.clone() );},
                  pybind11::arg( "return_code" ) = 0,
                  pybind11::arg( "return_message" ) = "",
                  pybind11::arg_v( "payload", scarab::param(), "scarab::param()" ),
                  "construct and send a reply message in response to this request",
                  DL_BIND_CALL_GUARD_STREAMS
                )
            ;

        /************
         msg_reply
         ************/
        all_items.push_back( "MsgReply" );
        pybind11::class_< dripline::msg_reply, msg_reply_trampoline, std::shared_ptr< dripline::msg_reply >
                        >( mod, "MsgReply", message, "dripline messages containing a reply to a previously received request" )
            // constructor(s)
            .def( pybind11::init< >() )

            // conversion to string
            .def( "__str__", [](dripline::reply_ptr_t a_rep){
              scarab::param_node t_encoding_options;
              t_encoding_options.add( "style", "pretty" );
              return a_rep->encode_full_message(5000, t_encoding_options);
            } )

            // properties
            // mv_referrable
            .def_property( "return_message", (std::string& (dripline::msg_reply::*)()) &dripline::msg_reply::return_message,
                           []( dripline::msg_reply& an_obj, const std::string& a_msg ){ an_obj.return_message() = a_msg; } )
            // mv_accessible
            .def_property( "return_code", &dripline::msg_reply::get_return_code, &dripline::msg_reply::set_return_code )

            // general methods
            //TODO the C++ interface has two more overloads where the input return code is a dripline::return_code;
            //     if we wrap that then we should add those overloads. (are we going to want to do that?)
            .def_static( "create",
                         [](unsigned a_retcode_value,
                            const std::string& a_ret_msg,
                            scarab::param& a_payload,
                            std::string& a_routing_key,
                            std::string& a_specifier,
                            dripline::message::encoding an_encoding)
                           {return dripline::msg_reply::create( a_retcode_value, a_ret_msg, a_payload.clone(), a_routing_key, a_specifier, an_encoding);},
                         pybind11::arg( "return_code" ) = 0,
                         pybind11::arg( "return_message" ) = "",
                         pybind11::arg( "payload" ) = scarab::param(),
                         pybind11::arg( "routing_key" ) = "",
                         pybind11::arg( "specifier" ) = "",
                         pybind11::arg( "encoding" ) = dripline::message::encoding::json,
                         "create and populate a new MsgReply instance",
                         DL_BIND_CALL_GUARD_STREAMS
                       )
            .def_static( "create",
                         [](unsigned a_retcode_value,
                            const std::string& a_ret_msg,
                            scarab::param& a_payload,
                            const dripline::msg_request& a_msg_request)
                           {return dripline::msg_reply::create( a_retcode_value, a_ret_msg, a_payload.clone(), a_msg_request);},
                         pybind11::arg( "return_code" ) = 0,
                         pybind11::arg( "return_message" ) = "",
                         pybind11::arg( "payload" ) = scarab::param(),
                         pybind11::arg( "msg_request" ) = dripline::message::encoding::json,
                         "create and populate a new MsgReply instance",
                         DL_BIND_CALL_GUARD_STREAMS
                       )
            ;

        /***********
         msg_alert
         ************/
        all_items.push_back( "MsgAlert" );
        pybind11::class_< dripline::msg_alert, msg_alert_trampoline, std::shared_ptr< dripline::msg_alert >
                        >( mod, "MsgAlert", message, "dripline message containing alert information" )
            // constructor(s)
            .def( pybind11::init< >() )

            // conversion to string
            .def( "__str__", [](dripline::alert_ptr_t a_alert){
              scarab::param_node t_encoding_options;
              t_encoding_options.add( "style", "pretty" );
              return a_alert->encode_full_message(5000, t_encoding_options);
            } )

            // general methods
            .def_static( "create",
                         []( scarab::param& a_payload,
                             std::string& a_routing_key,
                             std::string& a_specifier,
                             dripline::message::encoding an_encoding)
                           {return dripline::msg_alert::create( a_payload.clone(), a_routing_key, a_specifier, an_encoding);},
                         pybind11::arg( "payload" ) = scarab::param(),
                         pybind11::arg( "routing_key" ) = "",
                         pybind11::arg( "specifier" ) = "",
                         pybind11::arg( "encoding" ) = dripline::message::encoding::json,
                         "create and populate a new MsgAlert instance",
                         DL_BIND_CALL_GUARD_STREAMS
                       )
            ;

    return all_items;

    } /* export_message */

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_MESSAGE */
