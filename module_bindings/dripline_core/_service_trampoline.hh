#ifndef DRIPLINE_PYBIND_SERVICE_TRAMPOLINE
#define DRIPLINE_PYBIND_SERVICE_TRAMPOLINE

#include "service.hh"

#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    // we need an extra class so that we can make private/protected methods public for binding
    class _service : public dripline::service, public pybind11::trampoline_self_life_support
    {
        public:
            //inherit constructor
            using dripline::service::service;

            //make methods public for use in overload macro
            using dripline::service::bind_keys;
            using dripline::core::bind_key;
            using dripline::service::on_request_message;

    };

    class _service_trampoline : public _service
    {
        public:
            using _service::_service; //inherit constructors
            //_service_trampoline(_service &&base) : _service(std::move(base)) {}

            // Local overrides
            bool bind_keys() override
            {
                PYBIND11_OVERRIDE( bool, _service, bind_keys, );
            }

            void run() override
            {
                PYBIND11_OVERRIDE( void, _service, run, );
            }

            //// Overrides from Endpoint
            // Overrides for virtual on_[messgate-type]_message()
            dripline::reply_ptr_t on_request_message( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERRIDE( dripline::reply_ptr_t, _service, on_request_message, a_request );
            }
            void on_reply_message( const dripline::reply_ptr_t a_reply ) override
            {
                PYBIND11_OVERRIDE( void, _service, on_reply_message, a_reply );
            }
            void on_alert_message( const dripline::alert_ptr_t a_alert ) override
            {
                PYBIND11_OVERRIDE( void, _service, on_alert_message, a_alert );
            }

            // Overrides for virtual do_[request-type]_request
            dripline::reply_ptr_t do_get_request( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERRIDE( dripline::reply_ptr_t, _service, do_get_request, a_request );
            }
            dripline::reply_ptr_t do_set_request( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERRIDE( dripline::reply_ptr_t, _service, do_set_request, a_request );
            }
            dripline::reply_ptr_t do_cmd_request( const dripline::request_ptr_t a_request ) override
            {
                PYBIND11_OVERRIDE( dripline::reply_ptr_t, _service, do_cmd_request, a_request );
            }

    };

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SERVICE_TRAMPOLINE */
