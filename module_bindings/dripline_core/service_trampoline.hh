#ifndef DRIPLINE_PYBIND_SERVICE_TRAMPOLINE
#define DRIPLINE_PYBIND_SERVICE_TRAMPOLINE

#include "service.hh"

namespace dripline_pybind
{
    class _service : public dripline::service
    {
        public:
            //inherit constructor
            using dripline::service::service;

            //make methods public for use in overload macro
            using dripline::service::bind_keys;
            using dripline::core::bind_key;

    };

    //class _service_trampoline : public dripline::service
    class _service_trampoline : public _service
    {
        public:
            using _service::_service; //inherit constructors
            // Local overrides
            bool bind_keys() override
            {
                pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERLOAD( bool, _service, bind_keys, );
            }

            //// Overrides from Endpoint
            // Overrides for virtual on_[messgate-type]_message()
            dripline::reply_ptr_t on_request_message( const dripline::request_ptr_t a_request ) override
            {
                pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERLOAD( dripline::reply_ptr_t, _service, on_request_message, a_request );
            }
            void on_reply_message( const dripline::reply_ptr_t a_reply ) override
            {
                pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERLOAD( void, _service, on_reply_message, a_reply );
            }
            void on_alert_message( const dripline::alert_ptr_t a_alert ) override
            {
                pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERLOAD( void, _service, on_alert_message, a_alert );
            }

            // Overrides for virtual do_[request-type]_request
            dripline::reply_ptr_t do_get_request( const dripline::request_ptr_t a_request ) override
            {
                pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERLOAD( dripline::reply_ptr_t, _service, do_get_request, a_request );
            }
            dripline::reply_ptr_t do_set_request( const dripline::request_ptr_t a_request ) override
            {
                pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERLOAD( dripline::reply_ptr_t, _service, do_set_request, a_request );
            }
            dripline::reply_ptr_t do_cmd_request( const dripline::request_ptr_t a_request ) override
            {
                pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERLOAD( dripline::reply_ptr_t, _service, do_cmd_request, a_request );
            }

    };

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_SERVICE_TRAMPOLINE */
