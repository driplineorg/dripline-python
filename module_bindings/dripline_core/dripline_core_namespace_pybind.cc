#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

// Include custom header files
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
// #include "run_simple_service_pybind.hh"
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

           Exported Functions and Classes

           core
    )pbdoc";

    std::list<std::string> all_members;

    // The bound classes belong in a submodule, create that
    py::module dripline_core_mod = dripline_mod.def_submodule("core", "Core dripline standard implementation classes");

    // Example documentation for export functions in core
    all_members.splice(all_members.end(), dripline_pybind::export_constants(dripline_core_mod, R"pbdoc(
        Constants
        ---------

        Functions to export constants.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_core(dripline_core_mod, R"pbdoc(
        Core
        ----

        Functions related to the core functionality of dripline.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_dripline_config(dripline_core_mod, R"pbdoc(
        Dripline Config
        ---------------

        Functions to handle config functionalities in dripline.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_endpoint(dripline_core_mod, R"pbdoc(
        Endpoint
        --------

        Functions to handle endpoint-related functionalities.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_error(dripline_core_mod, R"pbdoc(
        Error Handling
        --------------

        Functions for error handling.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_message(dripline_core_mod, R"pbdoc(
        Message Handling
        ----------------

        Functions to handle different message types.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_receiver(dripline_core_mod, R"pbdoc(
        Receiver
        --------

        Functions for receiving messages.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_return_codes(dripline_core_mod, R"pbdoc(
        Return Codes
        ------------

        Functions to handle return codes.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_scheduler(dripline_core_mod, R"pbdoc(
        Scheduler
        ---------

        Functions to manage scheduling tasks.
    )pbdoc"));

    // Uncomment if applicable
    // all_members.splice(all_members.end(), dripline_pybind::export_run_simple_service(dripline_core_mod));

    all_members.splice(all_members.end(), dripline_pybind::export_specifier(dripline_core_mod, R"pbdoc(
        Specifiers
        ----------

        Functions to handle specifiers in dripline.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_service(dripline_core_mod, R"pbdoc(
        Service
        -------

        Functions to manage services.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_throw_reply(dripline_core_mod, R"pbdoc(
        Reply Handling
        --------------

        Functions for handling replies.
    )pbdoc"));

    all_members.splice(all_members.end(), dripline_pybind::export_version_store(dripline_core_mod, R"pbdoc(
        Version Store
        -------------

        Functions to manage version storage.
    )pbdoc"));

    // Add __all__ attribute
    dripline_core_mod.attr("__all__") = all_members;

#ifdef VERSION_INFO
    dripline_core_mod.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    dripline_core_mod.attr("__version__") = "dev";
#endif
}
