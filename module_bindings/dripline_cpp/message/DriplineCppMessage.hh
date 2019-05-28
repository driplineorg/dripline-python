#include "message.hh"

#include "DriplineCppMessageVirtual.hh"

#include "pybind11/pybind11.h"

namespace dripline_cpp_pybind
{

    void ExportDriplineCppMessagePybind( pybind11::module& mod )
    {

        /********
         message
        ********/
        pybind11::class_<dripline::message, dripline::py_message> message (mod, "dripline_message");
        
        pybind11::enum_<dripline::message::encoding>(message, "encoding")
            .value("json", dripline::message::encoding::json)
            .export_values();

        message.def(pybind11::init< >( ))
               .def("is_request", &dripline::message::is_request)
               .def("is_reply", &dripline::message::is_reply)
               .def("is_alert", &dripline::message::is_alert);

        message.def_static("process_envelope", &dripline::message::process_envelope, "From AMQP to message object")
               .def("create_amqp_message", &dripline::message::create_amqp_message, "From message object to AMQP")
               .def("encode_message_body", &dripline::message::encode_message_body, "From message object to string");

        // TODO: problem with return type
/*
        message.def("mv_referrable", (int (dripline::message::*)(std::string, dripline::routing_key)) &dripline::message::mv_referrable)
               .def("mv_referrable", (int (dripline::message::*)(std::string, dripline::correlation_id)) &dripline::message::mv_referrable)
               .def("mv_referrable", (int (dripline::message::*)(std::string, dripline::reply_to) &dripline::message::mv_referrable)
               .def("mv_accessible", &dripline::message::mv_accessible)
               .def("mv_referrable", (int (dripline::message::*)(std::string, dripline::timestamp) &dripline::message::mv_referrable)

               .def("mv_referrable_const", (int (dripline::message::*)(std::string, dripline::sender_package) &dripline::message::mv_referrable_const)
               .def("mv_referrable_const", (int (dripline::message::*)(std::string, dripline::sender_exe) &dripline::message::mv_referrable_const)
               .def("mv_referrable_const", (int (dripline::message::*)(std::string, dripline::sender_version )&dripline::message::mv_referrable_const)
               .def("mv_referrable_const", (int (dripline::message::*)(std::string, dripline::sender_commit) &dripline::message::mv_referrable_const)
               .def("mv_referrable_const", (int (dripline::message::*)(std::string, dripline::sender_hostname) &dripline::message::mv_referrable_const)
               .def("mv_referrable_const", (int (dripline::message::*)(std::string, dripline::sender_username) &dripline::message::mv_referrable_const)
               .def("mv_referrable_const", (int (dripline::message::*)(std::string, dripline::sender_service_name) &dripline::message::mv_referrable_const)

               .def("mv_referrable_const", (int (dripline::message::*)(scarab::param_node, dripline::sender_info) &dripline::message::mv_referrable_const));
*/

/*
        message.def("parsed_specifier", (dripline::specifier& (dripline::message::*)())&dripline::message::parsed_specifier);
               .def("message_type", &dripline::message::message_type);
*/


        message.def("set_sender_package", &dripline::message::set_sender_package)
               .def("set_sender_exe", &dripline::message::set_sender_version)
               .def("set_sender_version", &dripline::message::set_sender_version)
               .def("set_sender_commit", &dripline::message::set_sender_commit)
               .def("set_sender_hostname", &dripline::message::set_sender_hostname)
               .def("set_sender_username", &dripline::message::set_sender_username)
               .def("set_sender_service_name", &dripline::message::set_sender_service_name)

               .def("set_sender_info", &dripline::message::set_sender_info);
/*
//
        message.def("payload", (scarab::param& (dripline::message::*)())&dripline::message::payload)
               .def("set_payload", &dripline::message::set_payload);

        // originally << - need better ones
        message.def("encoding_ostream", [](std::ostream& a_os, message::encoding a_enc) { a_os << a_enc })
               .def("message_ostream", [](std::ostream& a_os, const dripline::message& a_message) { a_os << a_message });
*/
/*
        /************
         msg_request
        ************
        pybind11::class_<dripline::msg_request, dripline::py_msg_request> msg_request (mod, "dripline_msg_request")
            .def(pybind11::init< >( ))

            .def_static("create", &dripline::msg_request::create)

            .def("is_request", &dripline::msg_request::is_request)
            .def("is_reply", &dripline::msg_request::is_reply)
            .def("is_alert", &dripline::msg_request::is_alert);

            .def("reply", &dripline::msg_request::reply)

            .def("message_type", &dripline::msg_request::message_type);

            //TODO: other 4 functions without return type
*/
    }
    
} /* namespace dripline_cpp_pybind */
