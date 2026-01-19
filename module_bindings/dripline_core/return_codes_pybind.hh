#ifndef DRIPLINE_PYBIND_RETURN_CODES
#define DRIPLINE_PYBIND_RETURN_CODES

#include "return_codes.hh"
#include "return_code_trampoline.hh"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include <string>

namespace dripline_pybind
{
    // Macro for binding dripline-cpp return codes; note, it uses local variables defined and scoped in this header
#define ADD_DRIPLINE_RET_CODE( cpp_name, py_name ) \
    all_items.push_back( "DL_" #py_name ); \
    pybind11::class_< dripline::dl_##cpp_name, dripline::return_code >( mod, "DL_" #py_name, "" ) \
        .def( pybind11::init<>() ) \
        .def_property_readonly( "value", &dripline::dl_##cpp_name::rc_value ) \
        .def_property_readonly( "name", &dripline::dl_##cpp_name::rc_name ) \
        .def_property_readonly( "description", &dripline::dl_##cpp_name::rc_description ) \
        ;

    std::list< std::string > export_return_codes( pybind11::module& mod )
    {

        std::list< std::string > all_items;

        all_items.push_back( "ReturnCode" );
        pybind11::class_< dripline::return_code, return_code_trampoline >( mod, "ReturnCode", "base class for return codes" )
            .def( pybind11::init<>() )
            .def_property_readonly( "value", &dripline::return_code::rc_value, "return code value" )
            .def_property_readonly( "name", &dripline::return_code::rc_name, "return code name" )
            .def_property_readonly( "description", &dripline::return_code::rc_description, "return code description" )
            ;

        all_items.push_back( "add_return_code" );
        mod.def( "add_return_code",
                 &dripline::add_return_code,
                 pybind11::arg("value"),
                 pybind11::arg("name"),
                 pybind11::arg("description")
                 );

        all_items.push_back( "get_return_code_values" );
        mod.def( "get_return_code_values", &dripline::get_return_code_values );
        all_items.push_back( "get_return_codes_map" );
        mod.def( "get_return_codes_map", &dripline::get_return_codes_map );

        // now bind all of the existing dripline return codes so we can use them
        //**********************************************************************
        /* Success and Warnings */
        ADD_DRIPLINE_RET_CODE( success, Success )

        ADD_DRIPLINE_RET_CODE( warning_no_action_taken, WarningNoActionTaken )
        ADD_DRIPLINE_RET_CODE( warning_deprecated_feature, WarningDeprecatedFeature )
        ADD_DRIPLINE_RET_CODE( warning_dry_run, WarningDryRun )
        ADD_DRIPLINE_RET_CODE( warning_offline, WarningOffline )
        ADD_DRIPLINE_RET_CODE( warning_sub_service, WarningSubService )

        /* 100s AMQP errors */
        ADD_DRIPLINE_RET_CODE( amqp_error, AmqpError )
        ADD_DRIPLINE_RET_CODE( amqp_error_broker_connection, AmqpErrorBrokerConnection )
        ADD_DRIPLINE_RET_CODE( amqp_error_routingkey_notfound, AmqpErrorRoutingkeyNotfound )

        /* 200s Resource errors */
        ADD_DRIPLINE_RET_CODE( resource_error, ResourceError )
        ADD_DRIPLINE_RET_CODE( resource_error_connection, ResourceErrorConnection )
        ADD_DRIPLINE_RET_CODE( resource_error_no_response, ResourceErrorNoResponse )
        ADD_DRIPLINE_RET_CODE( resource_error_sub_service, ResourceErrorSubService )

        /* 300s Service errors */
        ADD_DRIPLINE_RET_CODE( service_error, ServiceError )
        ADD_DRIPLINE_RET_CODE( service_error_no_encoding, ServiceErrorNoEncoding )
        ADD_DRIPLINE_RET_CODE( service_error_decoding_fail, ServiceErrorDecodingFail )
        ADD_DRIPLINE_RET_CODE( service_error_bad_payload, ServiceErrorBadPayload )
        ADD_DRIPLINE_RET_CODE( service_error_invalid_value, ServiceErrorInvalidValue )
        ADD_DRIPLINE_RET_CODE( service_error_timeout, ServiceErrorTimeout )
        ADD_DRIPLINE_RET_CODE( service_error_invalid_method, ServiceErrorInvalidMethod )
        ADD_DRIPLINE_RET_CODE( service_error_access_denied, ServiceErrorAccessDenied )
        ADD_DRIPLINE_RET_CODE( service_error_invalid_key, ServiceErrorInvalidKey ) //lockout key
        ADD_DRIPLINE_RET_CODE( service_error_invalid_specifier, ServiceErrorInvalidSpecifier )

        /* 400s Client errors */
        ADD_DRIPLINE_RET_CODE( client_error, ClientError )
        ADD_DRIPLINE_RET_CODE( client_error_invalid_request, ClientErrorInvalidRequest )
        ADD_DRIPLINE_RET_CODE( client_error_handling_reply, ClientErrorHandlingReply )
        ADD_DRIPLINE_RET_CODE( client_error_unable_to_send, ClientErrorUnableToSend )
        ADD_DRIPLINE_RET_CODE( client_error_timeout, ClientErrorTimeout )

        /* 999 unhandled error */
        ADD_DRIPLINE_RET_CODE( unhandled_exception, UnhandledException )

        return all_items;
    }

}

#endif /* DRIPLINE_PYBIND_RETURN_CODES */
