#ifndef DRIPLINE_PYBIND_ERROR
#define DRIPLINE_PYBIND_ERROR

#include "dripline_exceptions.hh"
#include "message.hh"
#include "typename.hh"

#include "pybind11/pybind11.h"

#include <sstream>
#include <cxxabi.h>

namespace dripline_pybind
{
    // For use in tests of thowing exceptions on the C++ side
    void throw_dripline_error( const std::string& what_msg = "" )
    {
        throw dripline::dripline_error() << what_msg;
    }

    // For use in tests of throwing messages on the C++ side (this is done in core::do_send())
    void throw_message()
    {
        throw dripline::msg_request::create(scarab::param_ptr_t(new scarab::param()), dripline::op_t::get, "hey");
    }

    // Utility function so we can load the string version of a message into an error message
    template< typename T >
    std::string stream_message_ptr_to_error_message( T a_ptr, const std::string& a_prefix )
    {
        std::stringstream sstr;
        sstr << a_prefix << *a_ptr;
        std::string error_msg(sstr.str());
        return std::string(sstr.str());
    }

    std::list< std::string > export_error( pybind11::module& mod )
    {
        std::list< std::string > all_items;

        // For use in tests thowing exceptions on the C++ side and catching them on the Python side
        all_items.push_back( "throw_dripline_error" );
        mod.def( "throw_dripline_error", &dripline_pybind::throw_dripline_error, 
            "Test function for throwing a dripline_error on the C++ side" );

        // For use in tests thowing messages on the C++ side and catching them on the Python side
        all_items.push_back( "throw_message" );
        mod.def( "throw_message", &dripline_pybind::throw_message, 
            "Test function for throwing a message on the C++ side" );

        // Exception and exception translator registrations go below here.
        // Per Pybind11 docs, exception translation happens in reverse order from how they appear here.
        // Therefore we put the register_exception_translator try/catch block first, because it has a catch-all term for unknown exception types.
        // Within the try-catch block, we start with known classes that we want to catch, and finish with the `...` catch-all.
        // Following that, we have registered exceptions of known type.
/*
        // this static definition is used for the C++ --> Python throw_reply translation
        PYBIND11_CONSTINIT static py::gil_safe_call_once_and_store<py::object> throw_reply_storage;
        throw_reply_storage.call_once_and_store_result(
            [&]() { return dripline.core.ThrowReply; }
        );        
*/
        pybind11::register_exception_translator( [](std::exception_ptr p)
        {
            try
            {
                if ( p ) std::rethrow_exception( p );
            }
/*
            catch ( const dripline::throw_reply& e )
            {
                // Usually throw replies go Python --> C++, but this is here in case there's a C++ --> Python situation
                pybind11::set_error( dripline.core.ThrowReply )
            }
*/
            catch ( const dripline::message_ptr_t& e )
            {
                std::string error_msg = std::move(stream_message_ptr_to_error_message(e, "Thrown message:\n"));
                //std::cerr << "Caught message thrown:\n" << error_msg << std::endl;
                pybind11::set_error( PyExc_RuntimeError, error_msg.c_str() );
            }
            catch ( const dripline::request_ptr_t& e )
            {
                std::string error_msg = std::move(stream_message_ptr_to_error_message(e, "Thrown request:\n"));
                //::cerr << "Caught request thrown:\n" << error_msg << std::endl;
                pybind11::set_error( PyExc_RuntimeError, error_msg.c_str() );
            }
            catch ( const dripline::reply_ptr_t& e )
            {
                std::string error_msg = std::move(stream_message_ptr_to_error_message(e, "Thrown reply:\n"));
                //std::cerr << "Caught reply thrown:\n" << error_msg << std::endl;
                pybind11::set_error( PyExc_RuntimeError, error_msg.c_str() );
            }
            catch ( const dripline::alert_ptr_t& e )
            {
                std::string error_msg = std::move(stream_message_ptr_to_error_message(e, "Thrown alert:\n"));
                //std::cerr << "Caught alert thrown:\n" << error_msg << std::endl;
                pybind11::set_error( PyExc_RuntimeError, error_msg.c_str() );
            }
            catch (...) 
            {
                // catch-all for unknown exception types
                std::string exName(abi::__cxa_current_exception_type()->name());
                std::stringstream sstr;
                sstr << "Unknown exception: " << exName;
                std::string error_msg(sstr.str());
                //std::cerr << error_msg << std::endl;
                pybind11::set_error( PyExc_RuntimeError, error_msg.c_str() );
            }
        }
        );

        all_items.push_back( "DriplineError" );
        pybind11::register_exception< dripline::dripline_error >( mod, "DriplineError", PyExc_RuntimeError );
        

        return all_items;
    }

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_ERROR */
