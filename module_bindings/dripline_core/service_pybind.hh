#include "service.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{
    void export_service( pybind11::module& mod )
    {
        pybind11::class_< dripline::service, std::shared_ptr< dripline::service > >( mod, "service", "Binding for service" )
                .def( pybind11::init< const scarab::param_node&, const std::string&, const std::string&, const unsigned int, const std::string&, const bool >() )
                .def( "start", &dripline::service::start )
                .def( "listen", &dripline::service::listen )
                .def( "stop", &dripline::service::stop )
                .def( "add_child", &dripline::service::add_child )
                .def( "add_async_child", &dripline::service::add_async_child );

    } //end export_service
} //end dripline_pybind namespace
