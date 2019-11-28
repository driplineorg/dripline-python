#include "_return_code_trampoline.hh"

namespace dripline_pybind
{
    unsigned dl_bind_return_code::s_value = 0;
    std::string dl_bind_return_code::s_name( "bind_return_code" );
    std::string dl_bind_return_code::s_description( "base class for python-defined codes" );
} /* namespace dripline_pybind */
