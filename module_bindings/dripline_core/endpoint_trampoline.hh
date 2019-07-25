#ifndef DRIPLINE_PYBIND_ENDPOINT_TRAMPOLINE
#define DRIPLINE_PYBIND_ENDPOINT_TRAMPOLINE

#include "endpoint.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{

    class endpoint_trampoline : public dripline::endpoint
    {

        public:
            using dripline::endpoint::endpoint;

            // Override for virtual do_get_request
            dripline::reply_ptr_t do_get_request( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERLOAD( dripline::reply_ptr_t, dripline::endpoint, do_get_request, a_request );
            }

            // Override for virtual do_set_request
            dripline::reply_ptr_t do_set_request( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERLOAD( dripline::reply_ptr_t, dripline::endpoint, do_set_request, a_request );
            }

            // Override for virtual do_cmd_request
            dripline::reply_ptr_t do_cmd_request( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERLOAD( dripline::reply_ptr_t, dripline::endpoint, do_cmd_request, a_request );
            }

            std::string test_function( dripline::endpoint *an_endpoint ) override
            {
                PYBIND11_OVERLOAD( std::string, dripline::endpoint, test_function, an_endpoint );
            }
    };
    
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_ENDPOINT_TRAMPOLINE */
