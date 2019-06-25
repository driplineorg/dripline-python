#include "dripline_error.hh"

#include "pybind11/pybind11.h"

namespace dripline_pybind
{

    void export_error( pybind11::module& mod )
    {

        static pybind11::exception<dripline::dripline_error> ex(mod, "dripline_error");
        pybind11::register_exception_translator([](std::exception_ptr p) {
            try {
                if (p) std::rethrow_exception(p);
            } catch (const dripline::dripline_error &e) {
        // Set dripline_error as the active python error
                ex(e.what());
            }
        });

    }

} /* namespace dripline_pybind */
