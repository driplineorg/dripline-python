#include "message.hh"

#include "pybind11/pybind11.h"

namespace dripline_cpp_pybind
{

    void ExportDriplineCppMessagePybind( pybind11::module& mod )
    {

        pybind11::class_<dripline::dripline_message>(mod, "dripline_message");
        
        pybind11::enum_<dripline::dripline_message::encoding>(dripline::dripline_message, "encoding")
            .value("json", dripline::dripline_message::encoding::json)
            .export_values();

        mod.def(pybind11::init< >( ));
           // no destructor needed...?
           // TODO: pure virtual function * 3

        
        mod.def_static("process_envelope", &dripline::dripline_message::process_envelope, "From AMQP to message object")
           .def("create_amqp_message", &dripline::dripline_message::create_amqp_message, "From message object to AMQP")
           .def("encode_message_body", &dripline::dripline_message::encode_message_body, "From message object to string");

       // TODO: protected function * 3


       // TODO: smart pointers
       mod.def("mv_referrable", pybind11::overload_cast<std::string, dripline::routing_key>(&dripline::dripline_message::mv_referrable))
          .def("mv_referrable", pybind11::overload_cast<std::string, dripline::correlation_id>(&dripline::dripline_message::mv_referrable))
          .def("mv_referrable", pybind11::overload_cast<std::string, dripline::reply_to>(&dripline::dripline_message::mv_referrable))
          .def("mv_accessible", &dripline::dripline_message::accessible)

/*
            mv_referrable( std::string, timestamp );


            mv_referrable_const( std::string, sender_package );

            mv_referrable_const( std::string, sender_exe );

            mv_referrable_const( std::string, sender_version );

            mv_referrable_const( std::string, sender_commit );

            mv_referrable_const( std::string, sender_hostname );

            mv_referrable_const( std::string, sender_username );

            mv_referrable_const( std::string, sender_service_name );

            mv_referrable_const( scarab::param_node, sender_info );



*/


    }
    
} /* namespace dripline_cpp_pybind */
