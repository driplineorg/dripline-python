#ifndef DRIPLINE_PYBIND_ENDPOINT_TRAMPOLINE
#define DRIPLINE_PYBIND_ENDPOINT_TRAMPOLINE

#include "endpoint.hh"

#include "pybind11/pybind11.h"

namespace dripline_pybind
{

    class _endpoint_trampoline : public dripline::endpoint
    {

        public:
            using dripline::endpoint::endpoint;

            // Overrides for virtual on_[messgate-type]_message()
            dripline::reply_ptr_t on_request_message( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERRIDE( dripline::reply_ptr_t, dripline::endpoint, on_request_message, a_request );
            }
            void on_reply_message( const dripline::reply_ptr_t a_reply ) override
            {
                PYBIND11_OVERRIDE( void, dripline::endpoint, on_reply_message, a_reply );
            }
            void on_alert_message( const dripline::alert_ptr_t a_alert ) override
            {
                PYBIND11_OVERRIDE( void, dripline::endpoint, on_alert_message, a_alert );
            }

            // Overrides for virtual do_[request-type]_request
            dripline::reply_ptr_t do_get_request( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERRIDE( dripline::reply_ptr_t, dripline::endpoint, do_get_request, a_request );
            }
            dripline::reply_ptr_t do_set_request( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERRIDE( dripline::reply_ptr_t, dripline::endpoint, do_set_request, a_request );
            }
            dripline::reply_ptr_t do_cmd_request( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERRIDE( dripline::reply_ptr_t, dripline::endpoint, do_cmd_request, a_request );
            }
    };

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_ENDPOINT_TRAMPOLINE */
