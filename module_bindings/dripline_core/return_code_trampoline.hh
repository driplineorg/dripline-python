#ifndef DRIPLINE_PYBIND_RETURN_CODE_TRAMPOLINE
#define DRIPLINE_PYBIND_RETURN_CODE_TRAMPOLINE

#include "return_codes.hh"

#include "pybind11/pybind11.h"

namespace dripline_pybind
{

    class return_code_trampoline : public dripline::return_code, public pybind11::trampoline_self_life_support
    {
        public:
            using dripline::return_code::return_code;

            unsigned rc_value() const override
            {
                PYBIND11_OVERRIDE_PURE( unsigned, dripline::return_code, rc_value );
            }

            std::string rc_name() const override
            {
                PYBIND11_OVERRIDE_PURE( std::string, dripline::return_code, rc_name );
            }

            std::string rc_description() const override
            {
                PYBIND11_OVERRIDE_PURE( std::string, dripline::return_code, rc_description );
            }

    };

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_RETURN_CODE_TRAMPOLINE */
