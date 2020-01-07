# CMakeLists.txt for dripline-python/module_bindings
# Authors: B.H. LaRoque, N.S. Oblath

# pybind11 bindings of dripline-cpp into dripline.core
set( PB_DRIPLINE_CORE_HEADERFILES
    dripline_core/_endpoint.hh
    dripline_core/_endpoint_trampoline.hh
    dripline_core/core_pybind.hh
    dripline_core/constants_pybind.hh
    dripline_core/dripline_config_pybind.hh
    dripline_core/error_pybind.hh
    dripline_core/message_pybind.hh
    dripline_core/message_virtual_pybind.hh
    dripline_core/receiver_pybind.hh
    dripline_core/return_codes.hh
    dripline_core/return_code_trampoline.hh
    dripline_core/return_code_functions.hh
    dripline_core/service_pybind.hh
    dripline_core/service_trampoline.hh
    dripline_core/scheduler_pybind.hh
    dripline_core/throw_reply_pybind.hh
    dripline_core/version_store_pybind.hh
)
set( PB_DRIPLINE_CORE_SOURCEFILES
    dripline_core/return_code_functions.cc
    dripline_core/dripline_core_namespace_pybind.cc
)
pybind11_add_module( _dripline ${PB_DRIPLINE_CORE_SOURCEFILES} )
target_link_libraries( _dripline PRIVATE ${FULL_LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
#install( TARGETS _dripline DESTINATION ${LIB_INSTALL_DIR} )
