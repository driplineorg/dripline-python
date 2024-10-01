#ifndef DRIPLINE_PYBIND_MESSAGE_TRAMPOLINE
#define DRIPLINE_PYBIND_MESSAGE_TRAMPOLINE

#include "message.hh"

#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    class message_trampoline : public dripline::message
    {
        public:
            using dripline::message::message; // Inheriting constructors

            bool is_request() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( bool, dripline::message, is_request, );
            }

            bool is_reply() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( bool, dripline::message, is_reply, );
            }

            bool is_alert() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( bool, dripline::message, is_alert, );
            }

            // don't know if we plan to override in python, but need this method to not be pure-virtual
            void derived_modify_amqp_message( dripline::amqp_message_ptr a_amqp_msg, AmqpClient::Table& a_properties ) const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( void, dripline::message, derived_modify_amqp_message, a_amqp_msg, a_properties );
            }

            void derived_modify_message_param( scarab::param_node& a_node ) const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( void, dripline::message, derived_modify_message_body, a_node );
            }

            dripline::msg_t message_type() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( dripline::msg_t, dripline::message, message_type, );
            }

    };

    class msg_request_trampoline : public dripline::msg_request
    {
        public:
            using dripline::msg_request::msg_request;

            bool is_request() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( bool, dripline::msg_request, is_request, );
            }

            bool is_reply() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE(bool, dripline::msg_request, is_reply, );
            }

            bool is_alert() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE(bool, dripline::msg_request, is_alert, );
            }

            dripline::msg_t message_type() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE(dripline::msg_t, dripline::msg_request, message_type, );
            }

    };

    class msg_reply_trampoline : public dripline::msg_reply
    {
        public:
            using dripline::msg_reply::msg_reply;

            bool is_request() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE(bool, dripline::msg_reply, is_request, );
            }

            bool is_reply() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( bool, dripline::msg_reply, is_reply, );
            }

            bool is_alert() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( bool, dripline::msg_reply, is_alert, );
            }

            dripline::msg_t message_type() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( dripline::msg_t, dripline::msg_reply, message_type, );
            }

    };

    class msg_alert_trampoline : public dripline::msg_alert
    {
        public:
            using dripline::msg_alert::msg_alert;

            bool is_request() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( bool, dripline::msg_alert, is_request, );
            }

            bool is_reply() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( bool, dripline::msg_alert, is_reply, );
            }

            bool is_alert() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( bool, dripline::msg_alert, is_alert, );
            }

            dripline::msg_t message_type() const override
            {
                //pybind11::gil_scoped_acquire t_acquire;
                PYBIND11_OVERRIDE_PURE( dripline::msg_t, dripline::msg_alert, message_type, );
            }

    };

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_MESSAGE_TRAMPOLINE */
