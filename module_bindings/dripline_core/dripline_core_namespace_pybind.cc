#include "constants_pybind.hh"
#include "error_pybind.hh"
#include "run_simple_service_pybind.hh"
#include "_endpoint.hh"
#include "endpoint_trampoline.hh"
//#include "DriplineCppMessage.hh"

PYBIND11_MODULE( dripline, dripline_mod )
{
    // The bound classes belong in a submodule, create that
    pybind11::module dripline_core_mod = dripline_mod.def_submodule( "core", "Core dripline standard implementation classes" );
    // Call exporters for the dripline.core namespace
    dripline_pybind::export_constants( dripline_core_mod );
    dripline_pybind::export_error( dripline_core_mod );
    dripline_pybind::export_run_simple_service( dripline_core_mod );
    dripline_pybind::export_endpoint( dripline_core_mod );
    //dripline_cpp_pybind::ExportDriplineCppMessagePybind( dripline_cpp_mod );
}

