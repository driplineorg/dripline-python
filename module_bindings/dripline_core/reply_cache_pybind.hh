#ifndef DRIPLINE_PYBIND_REPLY_CACHE_HH_
#define DRIPLINE_PYBIND_REPLY_CACHE_HH_

#include "reply_cache.hh"

#include "pybind11/pybind11.h"
#include "pybind11/iostream.h"

namespace dripline_pybind
{

    std::list< std::string>  export_throw_reply( pybind11::module& mod )
    {
        std::list< std::string > all_items;

        all_items.push_back( "set_reply_cache" );
        mod.def( "set_reply_cache",
                 [](const dripline::return_code& a_code, const std::string& a_message, const scarab::param& a_payload) {
                    dripline::set_reply_cache( a_code, a_message, a_payload.clone());
                 },
                 pybind11::arg( "return_code" ),
                 pybind11::arg( "return_message" ),
                 pybind11::arg( "payload" ),
                 "set the reply cache with the desired information"
            );

        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_REPLY_CACHE_HH_ */
