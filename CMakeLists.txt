cmake_minimum_required(VERSION 3.12) # v3.12 required for dripline-cpp
project( DriplinePy VERSION 3.10.1 )

find_package( pybind11 REQUIRED )

find_package( Dripline 2.3.0 CONFIG REQUIRED )

include_directories( BEFORE ${PROJECT_SOURCE_DIR}/module_bindings/dripline_core )

add_subdirectory( module_bindings )
