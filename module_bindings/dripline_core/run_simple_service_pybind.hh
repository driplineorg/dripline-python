#include "run_simple_service.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind {

  void export_run_simple_service(pybind11::module& mod){
    pybind11::class_<dripline::run_simple_service, std::shared_ptr<dripline::run_simple_service> >(mod, "run_simple_service")
      .def(pybind11::init<const scarab::param_node&>())
      .def("execute", &dripline::run_simple_service::execute);

  } //end export_run_simple_service
} //end dripline_pybind namespace
