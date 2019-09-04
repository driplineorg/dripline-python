#ifndef DRIPLINE_PYBIND_SCHEDULER
#define DRIPLINE_PYBIND_SCHEDULER

#include "pybind11/pybind11.h"
#include "pybind11/chrono.h" // privides std::chrono <-> datetime types

#include "scheduler.hh"

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
    pybind11::class_< dripline::scheduler<executor_t, clock_t> >( mod, "Scheduler", "schedule future function calls" )
        .def( pybind11::init<>() )
        //.def( "schedule", &dripline::scheduler<executor_t, clock_t>::schedule )
        .def( "schedule",
                (int (dripline::scheduler<executor_t, clock_t>::*)(executable_t, clock_t::time_point)) &dripline::scheduler<executor_t, clock_t>::schedule,
        /*
                pybind11::arg( "executable" ),
                pybind11::arg( "execution time [datetime.datetime]" ),
        */
                "schedule an action a specific future time"
            )
        .def( "unschedule", &dripline::scheduler<executor_t, clock_t>::unschedule, pybind11::arg( "id" ), "Cancel a scheduled function call by its id" )
        .def( "execute", &dripline::scheduler<executor_t, clock_t>::execute, "Start the timing thread which executes scheduled actions" )
        ;

    return all_items;
    } /* export_scheduler() */
} /* namespace dripline pybind */
#endif /* DRIPLINE_PYBIND_SCHEDULER */
