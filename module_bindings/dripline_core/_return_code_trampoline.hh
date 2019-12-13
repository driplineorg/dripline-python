#ifndef DRIPLINE_PYBIND_RETURN_CODE_TRAMPOLINE
#define DRIPLINE_PYBIND_RETURN_CODE_TRAMPOLINE

#include "return_codes.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    DEFINE_DL_RET_CODE( bind_return_code, DRIPLINE_API );

    /*
    struct _return_code_trampoline : public dripline::return_code
    {
        static unsigned s_value;// = 0;
        static std::string s_name;// = "";
        static std::string s_description;// = "";
        virtual ~_return_code_trampoline() {};
        virtual unsigned rc_value() const { return _return_code_trampoline::s_value; };
        virtual std::string rc_name() const { return _return_code_trampoline::s_name; };
        virtual std::string rc_description() const { return _return_code_trampoline::s_description; };
    };
    */
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_RETURN_CODE_TRAMPOLINE */
