cmake_minimum_required(VERSION 3.1)
project( DriplinePy VERSION 3.10.1 )

list( APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/dripline-cpp/scarab/cmake )
include( PackageBuilder )

pbuilder_prepare_project()

set_option( Scarab_BUILD_PYTHON TRUE )

pbuilder_add_submodule( Dripline dripline-cpp )

add_subdirectory( module_bindings )
