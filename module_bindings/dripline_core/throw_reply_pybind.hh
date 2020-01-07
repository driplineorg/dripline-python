#ifndef DRIPLINE_PYBIND_THROW_REPLY_HH_
#define DRIPLINE_PYBIND_THROW_REPLY_HH_

#include "reply_cache.hh"
#include "dripline_fwd.hh"
#include "endpoint.hh"

#include "pybind11/pybind11.h"
#include "pybind11/iostream.h"

namespace dripline_pybind
{
    /*
    struct base
    {
        base() {}
        virtual ~base() {}

        virtual std::string label() const
        {
            return std::string( "base" );
        }

        virtual void throw_exception() const
        {
            throw std::runtime_error( "Thrown from base" );
            return;
        }

        void execute() const
        {
            try
            {
                std::cout << "Class used: " << this->label() << std::endl;
                this->throw_exception();
            }
            catch( const pybind11::error_already_set& e )
            {
                std::cerr << "pybind11::error_already_set:\n" << e.what() << "-----" << std::endl;

                std::cerr << "Test whether the keyword matching works:" << std::endl;
                if( std::string(e.what()).substr(0, dripline::throw_reply::py_throw_reply_keyword().size()) == dripline::throw_reply::py_throw_reply_keyword() )
                {
                    std::cerr << "Yes, this has been determined to be a throw_reply" << std::endl;

                    reply_cache* t_reply_cache = reply_cache::get_instance();
                    if( t_reply_cache->ret_code().rc_value() == dl_success::s_value )
                    {
                        LINFO( dlog, "Replying with: " << t_reply_cache->return_message() );
                    }
                    else
                    {
                        LWARN( dlog, "Replying with: " << t_reply_cache->return_message() );
                    }
                    t_reply = a_request->reply( t_reply_cache->ret_code(),t_reply_cache->return_message() );
                    t_reply->set_payload( t_reply_cache->get_payload_ptr()->clone() );
                    // don't rethrow a throw_reply
                    // reply to be sent outside the catch block
                }
                else
                {
                    std::cerr << "No, this has been determined to be not-a-throw_reply" << std::endl;

                    // treat the python exception as a standard exception
                    LERROR( dlog, "Caught exception from Python: " << e.what() );
                    t_reply = a_request->reply( dl_unhandled_exception(), e.what() );
                    t_replier(); // send the reply before rethrowing
                    throw; // unhandled exceptions should rethrow because they're by definition unhandled
                }

            }
            catch( const std::runtime_error& e )
            {
                std::cerr << "std::runtime_error:\n" << e.what() << "-----" << std::endl;
            }
            catch( const std::exception& e )
            {
                std::cerr << "std::exception:\n" << e.what() << "-----" << std::endl;
            }
        }

    };

    struct base_trampoline : base
    {
        using base::base;
        std::string label() const override
        {
            pybind11::gil_scoped_acquire t_acquire;
            PYBIND11_OVERLOAD( std::string, base, label );
        }
        void throw_exception() const override
        {
            pybind11::gil_scoped_acquire t_acquire;
            PYBIND11_OVERLOAD( void, base, throw_exception );
        }
    };

    struct _base : base
    {
        using base::label;
        using base::throw_exception;
    };

    void test_throw()
    {
        base the_base;
        the_base.execute();
        return;
    }
*/
    std::list< std::string>  export_throw_reply( pybind11::module& mod )
    {
        std::list< std::string > all_items;
/*
        all_items.push_back( "_Base" );
        pybind11::class_< base, base_trampoline >( mod, "_Base", "Base test class" )
            .def( pybind11::init<>() )
            .def( "label", &_base::label )
            .def( "throw_exception", &_base::throw_exception )
            .def( "execute", &base::execute )
            ;

        all_items.push_back( "test_throw" );
        mod.def( "test_throw", &test_throw );
*/

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
            .def_property( "return_message",
                            (std::string& (dripline::throw_reply::*)())&dripline::throw_reply::return_message,
                            [](dripline::throw_reply& a_throw, std::string& a_message){ a_throw.return_message() = a_message; },
                            pybind11::return_value_policy::reference_internal 
                         )
            .def_property( "return_code",
                           (dripline::return_code& (dripline::throw_reply::*)())&dripline::throw_reply::ret_code,
                           [](dripline::throw_reply& a_throw, dripline::return_code& a_code){ a_throw.set_return_code(a_code); },
                           pybind11::return_value_policy::reference_internal
                         )
            .def_property( "payload",
                           (scarab::param& (dripline::throw_reply::*)())&dripline::throw_reply::payload,
                           [](dripline::throw_reply& a_throw, scarab::param& a_payload){ a_throw.set_payload(a_payload.clone()); },
                           pybind11::return_value_policy::reference_internal
                         )
            ;
/*
        all_items.push_back( "set_reply_cache1" );
        mod.def( "set_reply_cache1",
                 (void (*)(const dripline::throw_reply&)) &dripline::set_reply_cache1,
                 pybind11::arg( "throw_reply" ),
                 "set the reply_cache with the desired throw_reply"
             );
*/
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

        //all_items.push_back( "throw_reply_keyword" );
        //mod.attr( "throw_reply_keyword" ) = TOSTRING(PYTHON_THROW_REPLY_KEYWORD);

        return all_items;
    }
} /* namespace dripline_pybind */

#endif /* DRIPLINE_PYBIND_THROW_REPLY_HH_ */
