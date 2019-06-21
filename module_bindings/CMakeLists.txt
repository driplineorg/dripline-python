
set( LIB_DEPENDENCIES Dripline_dripline_python )

# provided example
set( PB_EXAMPLE_HEADERFILES
)
set( PB_EXAMPLE_SOURCEFILES
    example.cc
)
pybind11_add_module( bind_example ${PB_EXAMPLE_SOURCEFILES} )
target_link_libraries( bind_example PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
pbuilder_install_libraries( bind_example )

# pybind11 bindings of scarab::param
set( PB_PARAM_HEADERFILES
    scarab_param/KTParamPybind.hh
)
set( PB_PARAM_SOURCEFILES
    scarab_param/scarab_param_namespace_pybind.cc
)
pybind11_add_module( scarab_param ${PB_PARAM_SOURCEFILES} )
target_link_libraries( scarab_param PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
pbuilder_install_libraries( scarab_param )

# pybind11 bindings of dripline-cpp into dripline.core
set( PB_DRIPLINE_CORE_HEADERFILES
    dripline_core/DriplineCppError.hh
    dripline_core/DriplineCppConstants.hh
    #dripline_core/DriplineCppMessage.hh
)
set( PB_DRIPLINE_CORE_SOURCEFILES
    dripline_core/dripline_core_namespace_pybind.cc
)
pybind11_add_module( dripline ${PB_DRIPLINE_CORE_SOURCEFILES} )
target_link_libraries( dripline PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
pbuilder_install_libraries( dripline)
