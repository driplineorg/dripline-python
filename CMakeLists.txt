cmake_minimum_required(VERSION 3.1)
project( DriplinePy VERSION 3.10.1 )

#list( APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/dripline-cpp/scarab/cmake )
#include( PackageBuilder )

#pbuilder_prepare_project()

#set_option( Dripline_BUILD_PYTHON TRUE )
#set( PYBIND11_INSTALL ON CACHE BOOL "Pybind11 option to install itself" FORCE )
#add_subdirectory( pybind11 )
#include_directories( pybind11/include )    
find_package( pybind11 REQUIRED )

# need yaml-cpp, which exports itself
##find_package( yaml-cpp CONFIG REQUIRED )
#set( SimpleAmqpClient_DIR "/usr/local/lib/cmake/DriplineCpp" )
#set( Scarab_DIR "/usr/local/lib/cmake/DriplineCpp" )
##find_package( SimpleAmqpClient CONFIG REQUIRED )
##find_package( Scarab CONFIG REQUIRED )
# then import DriplineCpp
#find_package(DriplineCpp 2.0.0 )
find_package( Dripline 2.3.0 CONFIG REQUIRED )

message( STATUS "dlcpp found: ${DriplineCpp_FOUND}" )
message( STATUS "dlcpp libraries: ${DriplineCpp_LIBRARIES}" )
message( STATUS "dlcpp include dirs: ${DriplineCpp_INCLUDE_DIRS}" )
message( STATUS "dlcpp version: ${DriplineCpp_VERSION}" )
if( TARGET Dripline::Dripline )
    message( STATUS "dlcpp target Dripline::Dripline exists" )
else()
    message( STATUS "dlcpp target Dripline::Dripline DOES NOT EXIST" )
endif()
   
message( STATUS "dlcpp library: ${DriplineCpp_LIBRARY}" )
message( STATUS "dlcpp include dir: ${DriplineCpp_INCLUDE_DIR}" )
   
message( STATUS "scarab library: ${Scarab_Dripline_LIBRARY}" )
   
message( STATUS "yaml-cpp libraries: ${YAML_CPP_LIBRARIES}" )
message( STATUS "yaml-cpp include dir: ${YAML_CPP_INCLUDE_DIR}" )

message( STATUS "##### python site packages: ${PYTHON_SITE_PACKAGES}" )
message( STATUS "##### python include dir: ${PYTHON_INCLUDE_DIRS}" )
message( STATUS "##### python prefix: ${PYTHON_PREFIX}" )

#include_directories( BEFORE ${DriplineCpp_INCLUDE_DIR} )

#pbuilder_add_submodule( Dripline dripline-cpp )

include_directories( BEFORE ${PROJECT_SOURCE_DIR}/module_bindings/dripline_core )

add_subdirectory( module_bindings )
