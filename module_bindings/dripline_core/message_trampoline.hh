#ifndef DRIPLINE_PYBIND_MESSAGE_TRAMPOLINE
#define DRIPLINE_PYBIND_MESSAGE_TRAMPOLINE

#include "message.hh"
#include "pybind11/pybind11.h"

namespace dripline
{
    class py_message : public message
    {
        public:
            using message::message; // Inheriting constructors

            bool is_request() const override
            {
                PYBIND11_OVERLOAD_PURE( bool, message, is_request, );
            }

            bool is_reply() const override
            {
                PYBIND11_OVERLOAD_PURE( bool, message, is_reply, );
            }

            bool is_alert() const override
            {
                PYBIND11_OVERLOAD_PURE( bool, message, is_alert, );
            }

            void derived_modify_amqp_message( amqp_message_ptr t_amqp_msg, AmqpClient::Table& a_properties ) const override
            {
                PYBIND11_OVERLOAD_PURE( void, message, derived_modify_amqp_message, t_amqp_msg, a_properties );
            }

            void derived_modify_message_param( scarab::param_node& a_node ) const override
            {
                PYBIND11_OVERLOAD_PURE( void, message, derived_modify_message_body, a_node );
            }

            msg_t message_type() const override
            {
                PYBIND11_OVERLOAD_PURE( msg_t, message, message_type, );
            }

    };

    class py_msg_request : public msg_request
    {
        public:
            using msg_request::msg_request;

            bool is_request() const override
            {
                PYBIND11_OVERLOAD_PURE( bool, msg_request, is_request,

                );
            }

            bool is_reply() const override
            {
                PYBIND11_OVERLOAD_PURE(bool, msg_request, is_reply,

                );
            }

            bool is_alert() const override
            {
                PYBIND11_OVERLOAD_PURE(bool, msg_request, is_alert,

                );
            }

            msg_t message_type() const override
            {
                PYBIND11_OVERLOAD_PURE(msg_t, msg_request, message_type,

                );
            }

    };

    class py_msg_reply : public msg_reply
    {
        public:
            using msg_reply::msg_reply;

            bool is_request() const override
            {
                PYBIND11_OVERLOAD_PURE(bool, msg_reply, is_request, );
            }

            bool is_reply() const override
            {
                PYBIND11_OVERLOAD_PURE( bool, msg_reply, is_reply, );
            }

            bool is_alert() const override
            {
                PYBIND11_OVERLOAD_PURE( bool, msg_reply, is_alert, );
            }

            msg_t message_type() const override
            {
                PYBIND11_OVERLOAD_PURE( msg_t, msg_reply, message_type, );
            }

    };

    class py_msg_alert : public msg_alert
    {
        public:
            using msg_alert::msg_alert;

            bool is_request() const override
            {
                PYBIND11_OVERLOAD_PURE( bool, msg_alert, is_request, );
            }

            bool is_reply() const override
            {
                PYBIND11_OVERLOAD_PURE( bool, msg_alert, is_reply, );
            }

            bool is_alert() const override
            {
                PYBIND11_OVERLOAD_PURE( bool, msg_alert, is_alert, );
            }

            msg_t message_type() const override
            {
                PYBIND11_OVERLOAD_PURE( msg_t, msg_alert, message_type, );
            }

    };

} /* namespace dripline */

#endif /* DRIPLINE_PYBIND_MESSAGE_TRAMPOLINE */
