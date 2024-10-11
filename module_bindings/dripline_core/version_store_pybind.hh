#ifndef DRIPLINE_PYBIND_VERSION_STORE
#define DRIPLINE_PYBIND_VERSION_STORE

#include "version_store.hh"

namespace dripline_pybind
{
    std::list< std::string> export_version_store( pybind11::module& mod )
    {
        std::list< std::string > all_members;
        all_members.push_back("add_version");
        mod.def( "add_version",
                 (void (*)(const std::string&, scarab::version_semantic_ptr_t)) &dripline::add_version,
                 pybind11::arg( "name" ),
                 pybind11::arg( "version" ),
                 "Add a scarab.SemanticVersion (version) to the dripline version_store singleton"
             );

        all_members.push_back("get_version");
        mod.def( "get_version",
                 (scarab::version_semantic_ptr_t (*)(const std::string& )) &dripline::get_version,
                 pybind11::arg( "name" ),
                 "Get a scarab.SemanticVersion (version) from the dripline version_store singleton"
             );
             
        return all_members;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_VERSION_STORE */
