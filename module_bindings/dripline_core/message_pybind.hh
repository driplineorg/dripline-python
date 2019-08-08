#ifndef DRIPLINE_PYBIND_MESSAGE
#define DRIPLINE_PYBIND_MESSAGE

#include "message.hh"
#include "message_trampoline.hh"
#include "pybind11/pybind11.h"
#include "pybind11/iostream.h"

#include "logger.hh"
LOGGER( dlog_mph, "message_pybind.hh" )

namespace dripline_pybind
{
    class _message : public dripline::message
    {
        public:
            using dripline::message::derived_modify_amqp_message;
            using dripline::message::derived_modify_message_param;
    };

    void export_message( pybind11::module& mod )
    {

        /********
         message
         ********/
        pybind11::class_< dripline::message, message_trampoline, std::shared_ptr< dripline::message > > message(mod, "Message");

        pybind11::enum_< dripline::message::encoding >( message, "encoding" )
                .value( "json", dripline::message::encoding::json )
                ;
        
        message.def( pybind11::init< >() )
                // methods to check message type
                .def( "is_request", &dripline::message::is_request, "Returns true if the message is a request, false otherwise" )
                .def( "is_reply", &dripline::message::is_reply, "Returns true if the message is a reply, false otherwise" )
                .def( "is_alert", &dripline::message::is_alert, "Returns true if the message is an alert, false otherwise" )
                // methods to convert between dripline message, amqp types, etc.
                /*.def_static( "process_envelope", &dripline::message::process_envelope,
                        "From AMQP to message object" ) */
                .def( "create_amqp_messages", &dripline::message::create_amqp_messages,
                        "From message object to AMQP",
                        pybind11::call_guard<pybind11::scoped_ostream_redirect,
                                       pybind11::scoped_estream_redirect>() )
                .def( "encode_message_body", &dripline::message::encode_message_body,
                        "From message object to string",
                        pybind11::call_guard<pybind11::scoped_ostream_redirect,
                                       pybind11::scoped_estream_redirect>() )
                .def( "derived_modify_amqp_message", &_message::derived_modify_amqp_message,
                        "derived_modify_amqp_message function",
                        pybind11::call_guard<pybind11::scoped_ostream_redirect,
                                       pybind11::scoped_estream_redirect>() )
                .def( "derived_modify_message_param", &_message::derived_modify_message_param,
                        "derived_modify_amqp_message function",
                        pybind11::call_guard<pybind11::scoped_ostream_redirect,
                                       pybind11::scoped_estream_redirect>() )
                // mv_referrable
                .def_property( "routing_key", (std::string& (dripline::message::*)()) &dripline::message::routing_key,
                           [](dripline::message& an_obj, const std::string& a_routing_key ){ an_obj.routing_key() = a_routing_key; } )
                /*.def( "get_routing_key", (std::string& (dripline::message::*)()) &dripline::message::routing_key,
                  "Returns the routing key of a message (the routing key determines where the message goes)" )*/
                .def_property( "correlation_id", (std::string& (dripline::message::*)()) &dripline::message::correlation_id,
                           [](dripline::message& an_obj, const std::string& a_correlation_id ){ an_obj.correlation_id() = a_correlation_id; } )
                .def_property( "reply_to", (std::string& (dripline::message::*)()) &dripline::message::reply_to,
                           [](dripline::message& an_obj, const std::string& a_reply_to ){ an_obj.reply_to() = a_reply_to; } )
                .def_property( "timestamp", (std::string& (dripline::message::*)()) &dripline::message::timestamp,
                           [](dripline::message& an_obj, const std::string& a_timestamp ){ an_obj.timestamp() = a_timestamp; } )
                // mv_accessible
                .def_property( "encoding", &dripline::message::get_encoding, &dripline::message::set_encoding )
                //.def( "get_encoding", (void (dripline::message::*)(dripline::message::encoding)) &dripline::message::get_encoding )
                // mv_referrable_const

                // Temporary removal, until  &dripline::message::<some_function> where <some_function> gets defined
                /*
                .def( "get_sender_package", &dripline::message::sender_package )
                .def( "get_sender_exe", &dripline::message::sender_exe )
                .def( "get_sender_version", &dripline::message::sender_version )
                .def( "get_sender_commit", &dripline::message::sender_commit )
                .def( "get_sender_hostname", &dripline::message::sender_hostname )
                .def( "get_sender_username", &dripline::message::sender_username )
                .def( "get_sender_service_name", &dripline::message::sender_service_name )
                .def( "get_sender_info", &dripline::message::sender_info )
                */
                .def( "parsed_specifier", (dripline::specifier& (dripline::message::*)())&dripline::message::parsed_specifier )
                .def( "message_type", &dripline::message::message_type )
                //Temporary removal, corresponding functions in message.hh are commented out
                /*
                .def( "set_sender_package", &dripline::message::set_sender_package )
                .def( "set_sender_exe", &dripline::message::set_sender_version )
                .def( "set_sender_version", &dripline::message::set_sender_version )
                .def( "set_sender_commit", &dripline::message::set_sender_commit )
                .def( "set_sender_hostname", &dripline::message::set_sender_hostname )
                .def( "set_sender_username", &dripline::message::set_sender_username )
                .def( "set_sender_service_name", &dripline::message::set_sender_service_name )
                .def( "set_sender_info", &dripline::message::set_sender_info )
                */
            .def( "payload", (scarab::param& (dripline::message::*)())&dripline::message::payload, pybind11::return_value_policy::reference_internal )
                //.def( "set_payload", &dripline::message::set_payload )

            .def( "encode_full_message", [](const dripline::message& a_message){ return a_message.encode_full_message(4000); } )
                ;

        /************
         msg_request
         ************/
        pybind11::class_< dripline::msg_request, msg_request_trampoline, std::shared_ptr< dripline::msg_request > > msg_request( mod, "MsgRequest", message );
        msg_request.def( pybind11::init< >() )
                .def_static( "create", [](){ return dripline::msg_request::create( scarab::param_ptr_t(new scarab::param()), dripline::op_t::unknown, "", "", "", dripline::message::encoding::json ); } )
            //.def_static( "create", &dripline::msg_request::create, 
                         //pybind11::arg( "a_payload" ),
                         //pybind11::arg( "a_msg_op" ) = dripline::op_t::unknown,
                         //pybind11::arg( "a_routing_key" ) = "",
                         //pybind11::arg( "a_specifier" ) = "",
                         //pybind11::arg( "a_reply_to" ) = "",
                         //pybind11::arg( "a_encoding" ) = dripline::message::encoding::json
                         //)
                .def( "is_request", &dripline::msg_request::is_request, "Returns true if the message is a request, false otherwise" )
                .def( "is_reply", &dripline::msg_request::is_reply, "Returns true if the message is a reply, false otherwise" )
                .def( "is_alert", &dripline::msg_request::is_alert, "Returns true if the message is an alert, false otherwise" )
                .def( "reply", [](dripline::request_ptr_t a_req){ return a_req->reply( 0, "", scarab::param_ptr_t(new scarab::param())); } )
                      //pybind11::arg( "a_retcode" ) = 0,
                      //pybind11::arg( "a_ret_msg" ) = "",
                      //pybind11::arg( "a_payload" ) = scarab::param_ptr_t(new scarab::param())
            //.def( "reply", (dripline::reply_ptr_t (dripline::msg_request::*)(const unsigned, const std::string&, scarab::param_ptr_t) const) &dripline::msg_request::reply )
                .def( "reply", [](dripline::request_ptr_t a_req, const unsigned a_retcode, const std::string& a_ret_msg){ return a_req->reply( a_retcode, a_ret_msg, scarab::param_ptr_t(new scarab::param())); } )
                .def( "reply", [](dripline::request_ptr_t a_req, const unsigned a_retcode, const std::string& a_ret_msg, scarab::param_node& a_payload)
                      {
                          //LDEBUG( dlog_mph, "Here is the payload: " << a_payload );
                          return a_req->reply( a_retcode, a_ret_msg, scarab::param_ptr_t(new scarab::param_node(a_payload)) );
                      } )
                .def( "message_type", &dripline::msg_request::message_type )

                // mv_accessible_static_noset
                .def_static( "get_message_type", &dripline::msg_request::get_message_type )
                // mv_referrable
                .def( "get_lockout_key", (boost::uuids::uuid& (dripline::msg_request::*)()) &dripline::msg_request::lockout_key )
                // mv_accessible
                .def( "get_lockout_key_valid", (void (dripline::msg_request::*)(bool)) &dripline::msg_request::get_lockout_key_valid )
            //.def_property( "lockout_key_valid", &dripline::msg_request::get_lockout_key_valid, &dripline::msg_request::set_lockout_key_valid)
                .def_property( "op_t", &dripline::msg_request::get_message_op, &dripline::msg_request::set_message_op )
                //.def( "get_message_op", (void (dripline::msg_request::*)(op_t)) &dripline::msg_request::get_message_op )
                ;

        /************
         msg_reply
         ************/
        pybind11::class_< dripline::msg_reply, msg_reply_trampoline, std::shared_ptr< dripline::msg_reply > > msg_reply( mod, "MsgReply", message );
        msg_reply.def( pybind11::init< >() )
                //.def_static( "create", (dripline::reply_ptr_t (dripline::msg_reply::*)(const dripline::return_code&, const std::string&, scarab::param_ptr_t, const std::string&, const std::string&, dripline::message::encoding)) &dripline::msg_reply::create, pybind11::arg("a_specifier") = "", pybind11::arg("a_encoding") = dripline::message::encoding::json )
                //.def_static( "create", (dripline::reply_ptr_t (dripline::msg_reply::*)(const dripline::return_code&, const std::string&, const dripline::msg_request&)) &dripline::msg_reply::create )
                //.def_static( "create", (dripline::reply_ptr_t (dripline::msg_reply::*)(unsigned, const std::string&, scarab::param_ptr_t, const std::string&, const std::string&, dripline::message::encoding)) &dripline::msg_reply::create, pybind11::arg("a_specifier") = "", pybind11::arg("a_encoding") = dripline::message::encoding::json )
                .def( "is_request", &dripline::msg_reply::is_request, "Returns true if the message is a request, false otherwise" )
                .def( "is_reply", &dripline::msg_reply::is_reply, "Returns true if the message is a reply, false otherwise" )
                .def( "is_alert", &dripline::msg_reply::is_alert, "Returns true if the message is an alert, false otherwise" )
                .def( "message_type", &dripline::msg_reply::message_type )
                // mv_accessible_static_noset
                .def_static( "get_message_type", &dripline::msg_reply::get_message_type )
                // mv_referrable
                .def( "get_return_msg", (std::string& (dripline::msg_reply::*)()) &dripline::msg_reply::return_msg )
                // mv_accessible
                .def( "get_return_code", (unsigned (dripline::msg_reply::*)()) &dripline::msg_reply::get_return_code )
                ;

        /***********
         msg_alert
         ************/
        pybind11::class_< dripline::msg_alert, msg_alert_trampoline, std::shared_ptr< dripline::msg_alert > > msg_alert( mod, "MsgAlert", message );
        msg_alert.def( pybind11::init< >() )
                //.def_static( "create", &dripline::msg_alert::create, pybind11::arg("a_specifier") = "", pybind11::arg("a_encoding") = dripline::message::encoding::json )
                .def( "is_request", &dripline::msg_alert::is_request, "Returns true if the message is a request, false otherwise" )
                .def( "is_reply", &dripline::msg_alert::is_reply, "Returns true if the message is a reply, false otherwise" )
                .def( "is_alert", &dripline::msg_alert::is_alert, "Returns true if the message is an alert, false otherwise" )
                .def( "message_type", &dripline::msg_alert::message_type )
                // mv_accessible_static_noset
                .def_static( "get_message_type", &dripline::msg_alert::get_message_type )
                ;

    } /* export_message */

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_MESSAGE */
