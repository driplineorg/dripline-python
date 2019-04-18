
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
