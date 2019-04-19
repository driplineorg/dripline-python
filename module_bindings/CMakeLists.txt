
# provided example
set( PB_EXAMPLE_HEADERFILES
)
set( PB_EXAMPLE_SOURCEFILES
    example.cc
)
set( LIB_DEPENDENCIES Dripline_dripline_python )
pybind11_add_module( bind_example ${PB_EXAMPLE_SOURCEFILES} )
target_link_libraries( bind_example PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
pbuilder_install_libraries( bind_example )

# param things
set( PB_PARAM_HEADERFILES
    scarab_param/KTParamPybind.hh
)
set( PB_PARAM_SOURCEFILES
    scarab_param/scarab_param_namespace_pybind.cc
)
pybind11_add_module( scarab_param ${PB_PARAM_SOURCEFILES} )
target_link_libraries( scarab_param PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
pbuilder_install_libraries( scarab_param )
