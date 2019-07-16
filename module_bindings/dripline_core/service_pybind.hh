#include "service.hh"
#include "pybind11/pybind11.h"
#include "pybind11/iostream.h"

namespace dripline_pybind
{
    void export_service( pybind11::module& mod )
    {
        pybind11::class_< dripline::service, std::shared_ptr< dripline::service > >( mod, "service", "Used to send and receive simple messages" )
                .def( pybind11::init< const scarab::param_node&, const std::string&, const std::string&, const unsigned int, const std::string&, const bool >(),
                        pybind11::call_guard<pybind11::scoped_ostream_redirect,
                                       pybind11::scoped_estream_redirect>() )
                .def( "start", &dripline::service::start,
                        pybind11::call_guard<pybind11::scoped_ostream_redirect,
                                       pybind11::scoped_estream_redirect>() )
                .def( "listen", &dripline::service::listen,
                        pybind11::call_guard<pybind11::scoped_ostream_redirect,
                                       pybind11::scoped_estream_redirect>() )
                .def( "stop", &dripline::service::stop,
                        pybind11::call_guard<pybind11::scoped_ostream_redirect,
                                       pybind11::scoped_estream_redirect>() )
                .def( "add_child", &dripline::service::add_child,
                        pybind11::call_guard<pybind11::scoped_ostream_redirect,
                                       pybind11::scoped_estream_redirect>() )
                .def( "add_async_child", &dripline::service::add_async_child,
                        pybind11::call_guard<pybind11::scoped_ostream_redirect,
                                       pybind11::scoped_estream_redirect>() )
                .def( "noisy_func", []() { pybind11::scoped_ostream_redirect stream(std::cout, pybind11::module::import("sys").attr("stdout"));});
    } //end export_service
} //end dripline_pybind namespace
