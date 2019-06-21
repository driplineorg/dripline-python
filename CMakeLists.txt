cmake_minimum_required(VERSION 3.1)
project( DriplinePy )

list( APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/dripline-cpp/scarab/cmake )
include( PackageBuilder )

add_subdirectory( pybind11 )

#add_subdirectory(dripline-cpp)
pbuilder_add_submodule( Dripline dripline-cpp )

add_subdirectory( module_bindings )

#pybind11_add_module(cmake_example src/main.cpp)
#target_link_libraries( cmake_example PRIVATE ${LIB_DEPENDENCIES} ${EXTERNAL_LIBRARIES} )
