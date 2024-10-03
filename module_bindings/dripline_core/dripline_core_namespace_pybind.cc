#include "pybind11/stl.h"

#include "constants_pybind.hh"
#include "core_pybind.hh"
#include "dripline_config_pybind.hh"
#include "_endpoint_pybind.hh"
#include "_endpoint_trampoline.hh"
#include "error_pybind.hh"
#include "message_pybind.hh"
#include "receiver_pybind.hh"
#include "reply_cache_pybind.hh"
#include "return_codes_pybind.hh"
#include "scheduler_pybind.hh"
//#include "run_simple_service_pybind.hh"
#include "specifier_pybind.hh"
#include "service_pybind.hh"
#include "version_store_pybind.hh"

namespace py = pybind11;

PYBIND11_MODULE(_dripline, dripline_mod) {
    // Module docstring
    dripline_mod.doc() = R"pbdoc(
        Dripline C++ Python bindings
        ----------------------------

        .. currentmodule:: _dripline

        .. autosummary::
           :toctree: _generate

           core
    )pbdoc";

    std::list<std::string> all_members;

    // The bound classes belong in a submodule, create that
    py::module dripline_core_mod = dripline_mod.def_submodule("core", "Core dripline standard implementation classes");

    // Call exporters for the dripline.core namespace with documentation
    all_members.splice(all_members.end(), dripline_pybind::export_constants(dripline_core_mod));
    all_members.splice(all_members.end(), dripline_pybind::export_core(dripline_core_mod));
    all_members.splice(all_members.end(), dripline_pybind::export_dripline_config(dripline_core_mod, R"pbdoc(
        Dripline Config
        ---------------
        
        Functionality related to the dripline configuration.
    )pbdoc"));
    all_members.splice(all_members.end(), dripline_pybind::export_endpoint(dripline_core_mod, R"pbdoc(
        Endpoint
        --------
        
        Endpoint related functionalities.
    )pbdoc"));
    all_members.splice(all_members.end(), dripline_pybind::export_error(dripline_core_mod, R"pbdoc(
        Error Handling
        --------------
        
        Error handling mechanisms.
    )pbdoc"));
    all_members.splice(all_members.end(), dripline_pybind::export_message(dripline_core_mod, R"pbdoc(
        Message Handling
        ----------------
        
        Handle different types of messages.
    )pbdoc"));
    all_members.splice(all_members.end(), dripline_pybind::export_receiver(dripline_core_mod, R"pbdoc(
        Receiver
        --------
        
        Functionality for receiving messages.
    )pbdoc"));
    all_members.splice(all_members.end(), dripline_pybind::export_return_codes(dripline_core_mod, R"pbdoc(
        Return Codes
        ------------
        
        Standardized return codes used in the module.
    )pbdoc"));
    all_members.splice(all_members.end(), dripline_pybind::export_scheduler(dripline_core_mod, R"pbdoc(
        Scheduler
        ---------
        
        Scheduling tasks and handling execution.
    )pbdoc"));
    // all_members.splice(all_members.end(), dripline_pybind::export_run_simple_service(dripline_core_mod));
    all_members.splice(all_members.end(), dripline_pybind::export_specifier(dripline_core_mod, R"pbdoc(
        Specifier
        ---------
        
        Specification of various components.
    )pbdoc"));
    all_members.splice(all_members.end(), dripline_pybind::export_service(dripline_core_mod, R"pbdoc(
        Service
        -------
        
        Service related functionalities.
    )pbdoc"));
    all_members.splice(all_members.end(), dripline_pybind::export_throw_reply(dripline_core_mod, R"pbdoc(
        Reply Handling
        --------------
        
        Handling replies to messages.
    )pbdoc"));
    all_members.splice(all_members.end(), dripline_pybind::export_version_store(dripline_core_mod, R"pbdoc(
        Version Store
        -------------
        
        Storing and managing versions.
    )pbdoc"));

    // Add __all__
    dripline_core_mod.attr("__all__") = all_members;

#ifdef VERSION_INFO
    dripline_core_mod.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    dripline_core_mod.attr("__version__") = "dev";
#endif
}
