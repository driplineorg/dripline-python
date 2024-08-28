#ifndef DRIPLINE_CONFIG_PYBIND_HH_
#define DRIPLINE_CONFIG_PYBIND_HH_

#include "dripline_config.hh"
#include "binding_helpers.hh"

#include "application.hh"

namespace dripline_pybind
{

    std::list< std::string> export_dripline_config( pybind11::module& mod )
    {
        std::list< std::string > all_members;

        all_members.push_back( "DriplineConfig" );
        pybind11::class_< dripline::dripline_config, scarab::param_node >( mod, "DriplineConfig" )
            .def( pybind11::init<>(), DL_BIND_CALL_GUARD_STREAMS )
            ;

        all_members.push_back( "add_dripline_options" );
        mod.def( "add_dripline_options", &dripline::add_dripline_options, 
                 "Add standard dripline CL options to a scarab.MainApp" );

        all_members.push_back( "add_dripline_auth_spec" );
        mod.def( "add_dripline_auth_spec", &dripline::add_dripline_auth_spec, 
                 pybind11::arg_v( "an_app", scarab::main_app(), "scarab.MainApp()" ),
                 pybind11::arg( "a_use_auth_file" ) = false,
                 "Add default dripline authentication specifications to a scarab.MainApp" );

        return all_members;
    }

} /* namespace dripline_pybind */

#endif /* DRIPLINE_CONFIG_PYBIND_HH_ */
