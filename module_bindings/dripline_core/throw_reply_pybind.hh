#ifndef DRIPLINE_PYBIND_THROW_REPLY_HH_
#define DRIPLINE_PYBIND_THROW_REPLY_HH_

#include "reply_cache.hh"
#include "dripline_fwd.hh"

#include "pybind11/pybind11.h"
#include "pybind11/iostream.h"

namespace dripline_pybind
{
    std::list< std::string>  export_throw_reply( pybind11::module& mod )
    {
        std::list< std::string > all_items;

        all_items.push_back( "_ThrowReply" );
        pybind11::class_< dripline::throw_reply >( mod, "_ThrowReply", "Holds information for creating a reply as a thrown exception")
            .def( pybind11::init<>() )
            .def( pybind11::init([]( const dripline::return_code& a_rc, scarab::param a_payload ) {
                    return std::unique_ptr< dripline::throw_reply >(new dripline::throw_reply( a_rc, a_payload.clone()));
                }),
                pybind11::arg( "return_code" ),
                pybind11::arg_v( "payload", scarab::param(), "Payload for the reply" )
            )
//            .def( pybind11::init< const dripline::return_code&,
//                                  scarab::param_ptr_t
//                                >(),
//                   pybind11::call_guard< pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect >(),
//                   pybind11::arg( "return_code" ),
//                   pybind11::arg_v( "payload", std::move(scarab::param_ptr_t(new scarab::param())), "Payload for the reply" )
//                )
            .def( pybind11::init< dripline::throw_reply >() )
            .def_property( "return_code",
                           (scarab::param& (dripline::throw_reply::*)())&dripline::throw_reply::ret_code,
                           [](dripline::throw_reply& a_throw, dripline::return_code& a_code){ a_throw.set_return_code(a_code); },
                           pybind11::return_value_policy::reference_internal
                         )
            .def_property( "payload",
                           (scarab::param& (dripline::throw_reply::*)())&dripline::throw_reply::payload,
                           [](dripline::throw_reply& a_throw, scarab::param& a_payload){ a_throw.set_payload(a_payload.clone()); },
                           pybind11::return_value_policy::reference_internal
                         )
            ;

        all_items.push_back( "set_reply_cache" );
        mod.def( "set_reply_cache",
                 (void (*)(const dripline::throw_reply&)) &dripline::set_reply_cache,
                 pybind11::arg( "throw_reply" ),
                 "set the reply_cache with the desired throw_reply"
             );


        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_THROW_REPLY_HH_ */
