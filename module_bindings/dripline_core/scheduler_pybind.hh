#ifndef DRIPLINE_PYBIND_SCHEDULER
#define DRIPLINE_PYBIND_SCHEDULER

#include "pybind11/pybind11.h"
#include "pybind11/chrono.h" // privides std::chrono <-> datetime types
#include "pybind11/functional.h"

#include "scheduler.hh"

#include "binding_helpers.hh"

namespace dripline_pybind
{
    std::list< std::string > export_scheduler( pybind11::module& mod )
    {
    std::list< std::string > all_items;

    all_items.push_back( "Scheduler" );
    // don't like this so much, should be a nicer way to deal with class tempalte...
    using executor_t = dripline::simple_executor;
    using executable_t = std::function< void() >;
    using clock_t = std::chrono::system_clock;
    pybind11::classh< dripline::scheduler< executor_t, clock_t >,
                      scarab::cancelable
                    >( mod, "Scheduler", "schedule future function calls" )
        .def( pybind11::init<>() )

        .def_property( "execution_buffer", &dripline::scheduler<executor_t, clock_t>::get_exe_buffer, &dripline::scheduler<executor_t, clock_t>::set_exe_buffer )
        .def_property( "cycle_time", &dripline::scheduler<executor_t, clock_t>::get_cycle_time, &dripline::scheduler<executor_t, clock_t>::set_cycle_time )
        //TODO: does it make sense to provide access to the events map? That will require wrapping the stuct they get stored into.

        .def( "schedule",
              (int (dripline::scheduler<executor_t, clock_t>::*)(executable_t, clock_t::time_point)) &dripline::scheduler<executor_t, clock_t>::schedule,
              DL_BIND_CALL_GUARD_STREAMS,
              pybind11::arg( "executable" ),
              pybind11::arg( "time" ),
              "schedule execution of executable at specified future time")
        .def( "schedule",
              (int (dripline::scheduler<executor_t, clock_t>::*)(executable_t, clock_t::duration, clock_t::time_point)) &dripline::scheduler<executor_t, clock_t>::schedule,
              DL_BIND_CALL_GUARD_STREAMS,
              pybind11::arg( "executable" ),
              pybind11::arg( "interval" ),
              pybind11::arg_v( "time", clock_t::now(), "now()" ),
              "schedule recurring execution of [executable] every [interval], starting at specified future [time]")
        .def( "unschedule",
              &dripline::scheduler<executor_t, clock_t>::unschedule,
              DL_BIND_CALL_GUARD_STREAMS,
              pybind11::arg( "id" ),
              "Cancel a scheduled function call by its id" )
        .def( "execute",
              &dripline::scheduler<executor_t, clock_t>::execute,
              DL_BIND_CALL_GUARD_STREAMS_AND_GIL, 
              "Start the timing thread which executes scheduled actions" )
        ;

    return all_items;
    } /* export_scheduler() */
} /* namespace dripline pybind */
#endif /* DRIPLINE_PYBIND_SCHEDULER */
