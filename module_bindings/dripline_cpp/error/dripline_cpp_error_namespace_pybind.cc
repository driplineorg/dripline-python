
#include "DriplineCppError.hh"

PYBIND11_MODULE( dripline_cpp_error, error_mod )
{
    dripline_cpp_pybind::ExportDriplineCppErrorPybind( error_mod );
}
