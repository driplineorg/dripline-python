#ifndef DRIPLINE_PYBIND_RETURN_CODES
#define DRIPLINE_PYBIND_RETURN_CODES

#include "return_codes.hh"
#include "return_code_trampoline.hh"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include <string>

namespace dripline_pybind
{
    LOGGER( dl_pybind_retcode, "return_codes_pybind" );
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

        ADD_DRIPLINE_RET_CODE( success, Success )

        ADD_DRIPLINE_RET_CODE( warning_no_action_taken, WarningNoActionTaken )

        ADD_DRIPLINE_RET_CODE( amqp_error, AmqpError )
        ADD_DRIPLINE_RET_CODE( amqp_error_broker_connection, AmqpErrorBrokerConnection )
        ADD_DRIPLINE_RET_CODE( amqp_error_routingkey_notfound, AmqpErrorRoutingkeyNotfound )

        ADD_DRIPLINE_RET_CODE( device_error, DeviceError )
        ADD_DRIPLINE_RET_CODE( device_error_connection, DeviceErrorConnection )
        ADD_DRIPLINE_RET_CODE( device_error_no_resp, DeviceErrorNoResp )

        ADD_DRIPLINE_RET_CODE( message_error, MessageError )
        ADD_DRIPLINE_RET_CODE( message_error_no_encoding, MessageErrorNoEncoding )
        ADD_DRIPLINE_RET_CODE( message_error_decoding_fail, MessageErrorDecodingFail )
        ADD_DRIPLINE_RET_CODE( message_error_bad_payload, MessageErrorBadPayload )
        ADD_DRIPLINE_RET_CODE( message_error_invalid_value, MessageErrorInvalidValue )
        ADD_DRIPLINE_RET_CODE( message_error_timeout, MessageErrorTimeout )
        ADD_DRIPLINE_RET_CODE( message_error_invalid_method, MessageErrorInvalidMethod )
        ADD_DRIPLINE_RET_CODE( message_error_access_denied, MessageErrorAccessDenied )
        ADD_DRIPLINE_RET_CODE( message_error_invalid_key, MessageErrorInvalidKey )
        ADD_DRIPLINE_RET_CODE( message_error_dripline_deprecated, MessageErrorDriplineDeprecated )
        ADD_DRIPLINE_RET_CODE( message_error_invalid_specifier, MessageErrorInvalidSpecifier )

        ADD_DRIPLINE_RET_CODE( client_error, ClientError )
        ADD_DRIPLINE_RET_CODE( client_error_invalid_request, ClientErrorInvalidRequest )
        ADD_DRIPLINE_RET_CODE( client_error_handling_reply, ClientErrorHandlingReply )
        ADD_DRIPLINE_RET_CODE( client_error_unable_to_send, ClientErrorUnableToSend )
        ADD_DRIPLINE_RET_CODE( client_error_timeout, ClientErrorTimeout )

        ADD_DRIPLINE_RET_CODE( unhandled_exception, UnhandledException )


        class return_code_registrar : public scarab::base_registrar< dripline::return_code >
        {
            public:
                return_code_registrar() {}
                virtual ~return_code_registrar() {}

                virtual dripline::return_code* create() const
                {
                    return new dripline::dl_unhandled_exception();
                }

                virtual unsigned value() const
                {
                    return dripline::dl_unhandled_exception::s_value;
                }
        };
        class return_code_registrar_trampoline : public return_code_registrar
        {
          public:
              using return_code_registrar::return_code_registrar;

              dripline::return_code* create() const override
              {
                pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERLOAD( dripline::return_code*, return_code_registrar, create );
              }
              unsigned value() const override
              {
                pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERLOAD( unsigned, return_code_registrar, value );
              }
        };

        all_items.push_back( "register_return_code" );
        mod.def( "register_return_code", [](return_code_registrar& a_registrar)
            {
                scarab::indexed_factory< unsigned, dripline::return_code >::get_instance()->register_class( a_registrar.value(), &a_registrar );
            },
            pybind11::call_guard< pybind11::gil_scoped_release >(),
            "Registers a new Dripline return code"
            );
        all_items.push_back( "get_return_codes" );
        mod.def( "get_return_codes",
                 [](){
                    std::list< unsigned > retcodes;
                    auto the_factory = scarab::indexed_factory< unsigned, dripline::return_code >::get_instance();
                    LDEBUG( dl_pybind_retcode, "factor is at " << the_factory );
                    auto anIt = the_factory->begin();
                    while (anIt != the_factory->end() )
                    {
                        retcodes.push_back( anIt->first );
                        anIt++;
                    }
                    retcodes.push_back(0);
                    return retcodes;
                    /*
                    return pybind11::make_iterator( the_registrar->begin(), the_registrar->end()
                      //scarab::indexed_factory< unsigned, dripline::return_code >::get_instance()->begin(),
                      //scarab::indexed_factory< unsigned, dripline::return_code >::get_instance()->end()
                    );
                    */
                 }//,
                // pybind11::keep_alive<0, 1>()
                 );


        //TODO: this probably needs a trampoline class to get the virtual functions to forward correctly
        all_items.push_back( "_ReturnCodeRegistrar" );
        pybind11::class_< return_code_registrar >( mod, "_ReturnCodeRegistrar", "base class for registering Python-based return codes" )
            .def( pybind11::init<>() )
            .def( "create", &return_code_registrar::create, "creates a new return code object" )
            .def( "value", &return_code_registrar::value, "returns the value of the return code" )
            ;
        /************************************************************
        //TODO: there should be a pure-python class ReturnCodeRegistrar that inherits from _ReturnCodeRegistrar
        //      it should store an instance of the class object of the return code
        //      it should implement create() and value()

        ***************************************************************/

        return all_items;
    }

}

#endif /* DRIPLINE_PYBIND_RETURN_CODES */
