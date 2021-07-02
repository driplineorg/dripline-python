cmake_minimum_required(VERSION 3.1)
project( DriplinePy VERSION 4.5.4 )

cmake_policy( SET CMP0074 NEW )

# standard install directories
include( GNUInstallDirs )

# We need to find Boost here so that all of the components have already been found 
# before each dependency's config
# Here's the master list of required boost components
# Requirements come from: SimpleAmqpClient, and Scarab
list( APPEND boost_components chrono filesystem system )
# Boost (1.47 required for SimpleAmqpClient)
find_package( Boost 1.47.0 REQUIRED COMPONENTS ${boost_components} )

set( PUBLIC_EXT_LIBS )

find_package( Threads REQUIRED )
list( APPEND PUBLIC_EXT_LIBS Threads::Threads )

find_package( pybind11 2.3.0 REQUIRED )
list( APPEND PUBLIC_EXT_LIBS pybind11::module )

find_package( Dripline 2.8.0 CONFIG REQUIRED )
list( APPEND PUBLIC_EXT_LIBS Dripline::Dripline Scarab::Scarab_Dripline )

include_directories( BEFORE ${PROJECT_SOURCE_DIR}/module_bindings/dripline_core )

add_subdirectory( module_bindings )
