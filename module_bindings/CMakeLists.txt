
set( LIB_DEPENDENCIES Dripline_DriplinePy DriplineExamples_DriplinePy )

# pybind11 bindings of scarab::param
set( PB_PARAM_HEADERFILES
    scarab_param/param_pybind.hh
    scarab_param/param_value.hh
    scarab_param/param_array.hh
    scarab_param/param_node.hh
)
set( PB_PARAM_SOURCEFILES
    scarab_param/scarab_param_namespace_pybind.cc
)
pybind11_add_module( scarab ${PB_PARAM_SOURCEFILES} )
target_link_libraries( scarab PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
pbuilder_install_libraries( scarab )

# pybind11 bindings of dripline-cpp into dripline.core
set( PB_DRIPLINE_CORE_HEADERFILES
    dripline_core/_endpoint.hh
    dripline_core/constants_pybind.hh
    dripline_core/endpoint_trampoline.hh
    dripline_core/error_pybind.hh
    dripline_core/message_pybind.hh
    dripline_core/message_virtual_pybind.hh
    dripline_core/run_simple_service_pybind.hh
)
set( PB_DRIPLINE_CORE_SOURCEFILES
    dripline_core/dripline_core_namespace_pybind.cc
)
pybind11_add_module( dripline ${PB_DRIPLINE_CORE_SOURCEFILES} )
target_link_libraries( dripline PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
pbuilder_install_libraries( dripline )
