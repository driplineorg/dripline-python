
#include "DriplineCppMessage.hh"

PYBIND11_MODULE( dripline_cpp_message, message_mod )
{
    dripline_cpp_pybind::ExportDriplineCppMessagePybind( message_mod );
}
