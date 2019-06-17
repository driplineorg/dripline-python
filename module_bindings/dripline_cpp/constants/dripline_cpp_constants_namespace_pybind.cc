
#include "DriplineCppConstants.hh"

PYBIND11_MODULE( dripline_cpp_constants, constants_mod )
{
    dripline_cpp_pybind::ExportDriplineCppConstantsPybind( constants_mod );
}
