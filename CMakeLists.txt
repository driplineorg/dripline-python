cmake_minimum_required(VERSION 3.1)
project( DriplinePy VERSION 4.4.6 )

list( APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/dripline-cpp/scarab/cmake )
include( PackageBuilder )

pbuilder_prepare_project()

set_option( Dripline_BUILD_PYTHON TRUE )

message( STATUS "##### python site packages: ${PYTHON_SITE_PACKAGES}" )
message( STATUS "##### python include dir: ${PYTHON_INCLUDE_DIRS}" )
message( STATUS "##### python prefix: ${PYTHON_PREFIX}" )

pbuilder_add_submodule( Dripline dripline-cpp )

include_directories( BEFORE ${PROJECT_SOURCE_DIR}/module_bindings/dripline_core )
add_subdirectory( module_bindings )
