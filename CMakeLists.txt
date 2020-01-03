cmake_minimum_required(VERSION 3.1)
project( DriplinePy VERSION 3.10.1 )

list( APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/dripline-cpp/scarab/cmake )
include( PackageBuilder )

pbuilder_prepare_project()

#set_option( Scarab_BUILD_PYTHON TRUE )
set_option( Dripline_BUILD_PYTHON TRUE )

pbuilder_add_submodule( Dripline dripline-cpp )

include_directories( BEFORE ${PROJECT_SOURCE_DIR}/module_bindings/dripline_core )
add_subdirectory( module_bindings )
