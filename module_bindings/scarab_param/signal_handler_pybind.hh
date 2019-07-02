#include "signal_handler.hh"

#include "pybind11/pybind11.h"

namespace scarab_pybind
{
    void export_signal_handler( pybind11::module& mod )
    {
        mod.def( "cancel_all", [](int a_code){ return scarab::signal_handler::cancel_all( a_code ); },
                   "Asynchronous call to exit the process with the given exit code" );
    }
} /* namespace scarab_pybind */
