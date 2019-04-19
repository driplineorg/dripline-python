/*
 * scarab_param_namespace_pybind.cc
 *
 * Created on: April 18, 2019
 *     Author: B.H. LaRoque
 */

#include "KTParamPybind.hh"

PYBIND11_MODULE( scarab_param, param_mod )
{
    scarab_pybind::ExportParamPybind( param_mod );
}
