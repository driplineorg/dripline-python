
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

## pybind11 bindings of dripline_cpp
#set( PB_DRIPLINE_CPP_HEADERFILES
#    dripline_cpp/DriplineCppError.hh
#    dripline_cpp/DriplineCppConstants.hh
#    dripline_cpp/DriplineCppMessage.hh
#)
#set( PB_DRIPLINE_CPP_SOURCEFILES
#    dripline_cpp/dripline_cpp_namespace_pybind.cc
#)
#pybind11_add_module( dripline_cpp ${PB_DRIPLINE_CPP_SOURCEFILES} )
#pbuilder_install_headers( ${PB_DRIPLINE_CPP_HEADERFILES} )
#target_link_libraries( dripline_cpp PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
#pbuilder_install_libraries( dripline_cpp )

