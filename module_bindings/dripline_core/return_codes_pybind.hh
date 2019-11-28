#ifndef DRIPLINE_PYBIND_RETURN_CODE
#define DRIPLINE_PYBIND_RETURN_CODE

#include "return_codes.hh"
#include "_return_code_trampoline.hh"

namespace dripline_pybind
{

    /*
    struct _return_code : public dripline::return_code
    {
        virtual unsigned _return_code::rc_value;
        virtual std::string _return_code::rc_name;
        virtual std::string _return_code::rc_description;
    };
    */

    std::list< std::string > export_return_codes( pybind11::module& mod )
    {
        std::list< std::string > all_members;

        all_members.push_back( "ReturnCode" );
        pybind11::class_< dripline_pybind::dl_bind_return_code/*, dripline_pybind::_return_code_trampoline*/ >( mod, "ReturnCode", "Base class for dripline return code objects" )
            .def_property_readonly( "rc_value", &dl_bind_return_code::rc_value )
            .def_property_readonly( "rc_name", &dl_bind_return_code::rc_name )
            .def_property_readonly( "rc_description", &dl_bind_return_code::rc_description )
            ;

        all_members.push_back( "DL_Success" );
        pybind11::class_< dripline::dl_success >( mod, "DL_Success", "Success return code" );

        return all_members;
    }

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_RETURN_CODE */
