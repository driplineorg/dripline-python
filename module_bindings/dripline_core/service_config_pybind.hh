#ifndef SERVICE_CONFIG_PYBIND_HH_
#define SERVICE_CONFIG_PYBIND_HH_

#include "service_config.hh"
#include "binding_helpers.hh"

#include "application.hh"

namespace dripline_pybind
{

    std::list< std::string> export_service_config( pybind11::module& mod )
    {
        std::list< std::string > all_members;

        all_members.push_back( "ServiceConfig" );
        // scarab::param_node uses class_, so we don't use classh here
        pybind11::class_< dripline::service_config, scarab::param_node >( mod, "ServiceConfig" )
            .def( pybind11::init< const std::string& >(), 
                  DL_BIND_CALL_GUARD_STREAMS,
                  pybind11::arg( "name" ) = "dlpy_service" 
                )
            ;

        all_members.push_back( "add_service_options" );
        mod.def( "add_service_options", &dripline::add_service_options, 
                 "Add service CL options to a scarab.MainApp" );

        return all_members;
    }

} /* namespace dripline_pybind */

#endif /* SERVICE_CONFIG_PYBIND_HH_ */
