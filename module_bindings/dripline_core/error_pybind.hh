#ifndef DRIPLINE_PYBIND_ERROR
#define DRIPLINE_PYBIND_ERROR

#include "dripline_exceptions.hh"
#include "pybind11/pybind11.h"

namespace dripline_pybind
{

    std::list< std::string > export_error( pybind11::module& mod )
    {
        std::list< std::string > all_items;

        //TODO how do we actually want to deal with errors?
        all_items.push_back( "DriplineError" );
        pybind11::register_exception< dripline::dripline_error >( mod, "DriplineError" );

        pybind11::register_exception_translator( [](std::exception_ptr p)
        {
            try
            {
                if ( p ) std::rethrow_exception( p );
            }
            catch ( const dripline::dripline_error &e )
            {
                // Set dripline_error as the active python error
                pybind11::set_error( PyExc_Exception, e.what() );
            }
        }
        );
        return all_items;
    }

} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_ERROR */
