cmake_minimum_required(VERSION 3.1)
project( DriplinePy )

list( APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/dripline-cpp/scarab/cmake )
include( PackageBuilder )

add_subdirectory( pybind11 )

pbuilder_add_submodule( Dripline dripline-cpp )

add_subdirectory( module_bindings )
