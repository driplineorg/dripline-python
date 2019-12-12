#ifndef DRIPLINE_PYBIND_RETURN_CODE_TRAMPOLINE
#define DRIPLINE_PYBIND_RETURN_CODE_TRAMPOLINE

#include "return_codes.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{

    class return_code_trampoline : public dripline::return_code
    {
        public:
            using dripline::return_code::return_code;

            unsigned rc_value() const override
            {
                PYBIND11_OVERLOAD_PURE( unsigned, dripline::return_code, rc_value );
            }

    };

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_RETURN_CODE_TRAMPOLINE */
