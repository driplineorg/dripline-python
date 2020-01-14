#ifndef DRIPLINE_PYBIND_BINDING_HELPERS
#define DRIPLINE_PYBIND_BINDING_HELPERS

#define DL_BIND_CALL_GUARD_STREAMS \
    pybind11::call_guard< pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect >()

#define DL_BIND_CALL_GUARD_STREAMS_AND_GIL \
    pybind11::call_guard< pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect, pybind11::gil_scoped_release >()

#endif /* DRIPLINE_PYBIND_BINDING_HELPERS */
