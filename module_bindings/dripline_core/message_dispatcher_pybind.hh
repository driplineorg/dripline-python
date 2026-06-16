#ifndef DRIPLINE_PYBIND_MESSAGE_DISPATCHER_HH_
#define DRIPLINE_PYBIND_MESSAGE_DISPATCHER_HH_

#include "binding_helpers.hh"

#include "message_dispatcher.hh"

#include "rmqt_queue.h"

#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    std::list< std::string > export_message_dispatcher( pybind11::module& mod )
    {
        std::list< std::string > all_members;

        all_members.push_back( "MessageDispatcher" );
        // message_dispatcher is abstract (submit_message() is pure-virtual), so no constructor is bound.
        // It must be registered here because it is listed as a base class of _Service.
        pybind11::classh< dripline::message_dispatcher, dripline::receiver >( mod, "MessageDispatcher",
            "Receives assembled Dripline messages from an AMQP consumer and dispatches them" )

            // Queue handle property
            .def_property( "queue",
                           &dripline::message_dispatcher::get_queue,
                           &dripline::message_dispatcher::set_queue,
                           "The QueueHandle for this dispatcher's AMQP queue. "
                           "Set by add_queues() (via add_requests_ephemeral_queue()), "
                           "and passed to start_listening() during listen()." )

            ;

        return all_members;
    }
} /* namespace dripline_pybind */
#endif /* DRIPLINE_PYBIND_MESSAGE_DISPATCHER_HH_ */
