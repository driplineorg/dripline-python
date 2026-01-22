#ifndef DRIPLINE_PYBIND_RECEIVER_HH_
#define DRIPLINE_PYBIND_RECEIVER_HH_

#include "binding_helpers.hh"

#include "receiver.hh"

#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    std::list< std::string > export_receiver( pybind11::module& mod )
    {
        std::list< std::string > all_members;

        all_members.push_back( "Receiver" );
        pybind11::classh< dripline::receiver, scarab::cancelable >( mod, "Receiver", "Collect and combine message chunks into a full message object")
            .def( pybind11::init<>() )

            .def_property( "single_message_wait_ms",
                  &dripline::receiver::get_single_message_wait_ms,
                  &dripline::receiver::set_single_message_wait_ms )

            .def( "wait_for_reply",
                  (dripline::reply_ptr_t (dripline::receiver::*)(const dripline::sent_msg_pkg_ptr, int)) &dripline::receiver::wait_for_reply,
                  pybind11::arg( "sent_msg_pkg" ),
                  pybind11::arg( "timeout_ms" ) = 0,
                  "wait for a reply message, if timeout_ms <=0, no timeout (default 0)",
                  DL_BIND_CALL_GUARD_STREAMS_AND_GIL )

            ;

        return all_members;
    }
} /* namespace dripline_pybind */
#endif /* DRIPLINE_PYBIND_RECEIVER_HH_ */
