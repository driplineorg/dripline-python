
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


# dripline_cpp_error
set( PB_DC_ERROR_HEADERFILES
    dripline_cpp/error/DriplineCppError.hh
)
set( PB_DC_ERROR_SOURCEFILES
    dripline_cpp/error/dripline_cpp_error_namespace_pybind.cc
)
pybind11_add_module( dripline_error ${PB_DC_ERROR_SOURCEFILES} )
target_link_libraries( dripline_error PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
pbuilder_install_libraries( dripline_error )


# dripline_cpp_constants
set( PB_DC_CONSTANTS_HEADERFILES
    dripline_cpp/constants/DriplineCppConstants.hh
)
set( PB_DC_CONSTANTS_SOURCEFILES
    dripline_cpp/constants/dripline_cpp_constants_namespace_pybind.cc
)

pybind11_add_module( dripline_constants ${PB_DC_CONSTANTS_SOURCEFILES} )
target_link_libraries( dripline_constants PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
pbuilder_install_libraries( dripline_constants )



# dripline_cpp_message
set( PB_DC_MESSAGE_HEADERFILES
    dripline_cpp/message/DriplineCppMessage.hh
)
set( PB_DC_MESSAGE_SOURCEFILES
    dripline_cpp/message/dripline_cpp_message_namespace_pybind.cc
)

pybind11_add_module( dripline_message ${PB_DC_MESSAGE_SOURCEFILES} )
target_link_libraries( dripline_message PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
pbuilder_install_libraries( dripline_message )
