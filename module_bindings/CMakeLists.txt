# CMakeLists.txt for dripline-python/module_bindings
# Authors: B.H. LaRoque, N.S. Oblath

# pybind11 bindings of dripline-cpp into dripline.core
set( PB_DRIPLINE_CORE_HEADERFILES
    dripline_core/_endpoint.hh
    dripline_core/_endpoint_trampoline.hh
    dripline_core/binding_helpers.hh
    dripline_core/core_pybind.hh
    dripline_core/constants_pybind.hh
    dripline_core/dripline_config_pybind.hh
    dripline_core/error_pybind.hh
    dripline_core/message_pybind.hh
    dripline_core/message_virtual_pybind.hh
    dripline_core/receiver_pybind.hh
    dripline_core/reply_cache_pybind.hh
    dripline_core/return_codes.hh
    dripline_core/return_code_trampoline.hh
    dripline_core/service_pybind.hh
    dripline_core/service_trampoline.hh
    dripline_core/scheduler_pybind.hh
    dripline_core/version_store_pybind.hh
)
set( PB_DRIPLINE_CORE_SOURCEFILES
    dripline_core/dripline_core_namespace_pybind.cc
)

pybind11_add_module( _dripline ${PB_DRIPLINE_CORE_SOURCEFILES} )

get_target_property( SOURCE_TREE_INCLUDE_DIRS _dripline INCLUDE_DIRECTORIES )
message( STATUS "Adding install interface include dir: ${CMAKE_INSTALL_INCLUDEDIR}" )
message( STATUS "Adding build interface include dirs: ${SOURCE_TREE_INCLUDE_DIRS}" )

target_include_directories( _dripline
    INTERFACE 
        "$<BUILD_INTERFACE:${SOURCE_TREE_INCLUDE_DIRS}>"
        "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
)

target_link_libraries( _dripline PUBLIC ${PUBLIC_EXT_LIBS} )

set( PY_MODULE_INSTALL_DIR ${CMAKE_INSTALL_LIBDIR} )
# Override that install location if specified by the user
if( INSTALL_DLPYBIND_IN_SITELIB AND DEFINED Python3_SITELIB )
    set( PY_MODULE_INSTALL_DIR ${Python3_SITELIB} )
endif( INSTALL_DLPYBIND_IN_SITELIB AND DEFINED Python3_SITELIB )
message( STATUS "Installing module _dripline in ${PY_MODULE_INSTALL_DIR}" )

install( TARGETS _dripline DESTINATION ${PY_MODULE_INSTALL_DIR} )
