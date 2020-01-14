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
                 "add a scarab.SemanticVersion (version) to the dripline version_store singleton"
             );
        return all_members;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_VERSION_STORE */
