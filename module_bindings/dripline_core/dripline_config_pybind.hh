#ifndef DRIPLINE_CONFIG_PYBIND_HH_
#define DRIPLINE_CONFIG_PYBIND_HH_

#include "dripline_config.hh"
#include "application.hh"

namespace dripline_pybind
{

    std::list< std::string> export_dripline_config( pybind11::module& mod )
    {
        std::list< std::string > all_members;

        all_members.push_back( "DriplineConfig" );
        pybind11::class_< dripline::dripline_config, scarab::param_node >( mod, "DriplineConfig" )
            .def( pybind11::init<>() )
            ;

        all_members.push_back( "add_dripline_options" );
        mod.def( "add_dripline_options", &dripline::add_dripline_options, "Add standard dripline options to a scarab.MainApp" );

        return all_members;
    }

} /* namespace dripline_pybind */

#endif /* DRIPLINE_CONFIG_PYBIND_HH_ */
