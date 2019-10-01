# CMakeLists.txt for dripline-python/module_bindings
# Authors: B.H. LaRoque, N.S. Oblath

# insert version information into the version source file
configure_file( dripline_core/dripline_python_version.cc.in ${CMAKE_CURRENT_BINARY_DIR}/dripline_python_version.cc )

# pybind11 bindings of dripline-cpp into dripline.core
set( PB_DRIPLINE_CORE_HEADERFILES
    dripline_core/_endpoint.hh
    dripline_core/_endpoint_trampoline.hh
    dripline_core/core_pybind.hh
    dripline_core/constants_pybind.hh
    dripline_core/dripline_config_pybind.hh
    dripline_core/dripline_python_version.hh
    dripline_core/error_pybind.hh
    dripline_core/message_pybind.hh
    dripline_core/message_virtual_pybind.hh
    dripline_core/scheduler_pybind.hh
    #dripline_core/run_simple_service_pybind.hh
    dripline_core/receiver_pybind.hh
    dripline_core/version_store_pybind.hh
)
set( PB_DRIPLINE_CORE_SOURCEFILES
    dripline_core/dripline_core_namespace_pybind.cc
    ${CMAKE_CURRENT_BINARY_DIR}/dripline_python_version.cc
)
pybind11_add_module( _dripline ${PB_DRIPLINE_CORE_SOURCEFILES} )
target_link_libraries( _dripline PRIVATE ${FULL_LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
install( TARGETS _dripline DESTINATION ${LIB_INSTALL_DIR} )
