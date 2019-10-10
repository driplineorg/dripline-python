
#include "return_codes.hh"

#include "pybind11/pybind11.h"

#include <string>

namespace dripline_pybind
{

    std::list< std::string > export_version( pybind11::module& mod )
    {
        class return_code_registrar : public scarab::base_registrar< dripline::return_code >
        {
            public:
                return_code_registrar() {}
                virtual ~return_code_registrar() {}

                virtual dripline::return_code* create() const
                {
                    return new dripline::dl_unhandled_exception();
                }

                virtual unsigned value() const
                {
                    return dripline::dl_unhandled_exception::s_value;
                }
        };


        std::list< std::string > all_items;

        all_items.push_back( "ReturnCode" );
        pybind11::class_< return_code >( mod, "ReturnCode", "base class for return codes" )
            .def( pybind11::init<>() )
            .def( "value", &return_code::value, "return code value" )
            .def( "name", &return_code::name, "return code name" )
            ;
            

        all_items.push_back( "register_return_code" );
        mod.def( "register_return_code", [](return_code_registrar& a_registrar){ 
                    scarab::indexed_factory< unsigned, dripline::return_code >::get_instance()->register_class( a_registrar.value(), &a_registrar ); 
            },
            pybind11::call_guard< pybind11::gil_scoped_release >(),
            "Registers a new Dripline return code" );

        //TODO: this probably needs a trampoline class to get the virtual functions to forward correctly
        all_items.push_back( "_ReturnCodeRegistrar" );
        pybind11::class_< return_code_registrar >( mod, "_ReturnCodeRegistrar", "base class for registering Python-based return codes" )
            .def( pybind11::init<>() )
            .def( "create", &return_code_registrar::create, "creates a new return code object" )
            .def( "value", &return_code_registrar::value, "returns the value of the return code" )
            ;

        //TODO: there should be a pure-python class ReturnCodeRegistrar that inherits from _ReturnCodeRegistrar
        //      it should store an instance of the class object of the return code
        //      it should implement create() and value()

        return all_items;
    }

}