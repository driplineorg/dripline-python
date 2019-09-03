/*
 * param_pybind.hh
 *
 *  Created on: Feb 1, 2018
 *      Author: N. Oblath, L. Gladstone, B.H. LaRoque
 */

#include "param.hh"
#include "error.hh"

#include "pybind11/pybind11.h"
#include "pybind11/pytypes.h"

namespace scarab_pybind
{
    scarab::param_ptr_t to_param( const pybind11::object& an_object )
    {
        using namespace pybind11;
        if( isinstance< none >( an_object ) )
        {
            return scarab::param_ptr_t( new scarab::param() );
        }
        else if( isinstance< bool_ >( an_object ) )
        {
            return scarab::param_ptr_t( new scarab::param_value( static_cast< const bool_& >(an_object) ) );
        }
        else if( isinstance< int_ >( an_object ) )
        {
            return scarab::param_ptr_t( new scarab::param_value( (int64_t)static_cast< const int_& >(an_object) ) );
        }
        else if( isinstance< float_ >( an_object ) )
        {
            return scarab::param_ptr_t( new scarab::param_value( (double)static_cast< const float_& >(an_object) ) );
        }
        else if( isinstance< str >( an_object ) )
        {
            return scarab::param_ptr_t( new scarab::param_value( static_cast< const str& >(an_object) ) );
        }
        else if( isinstance< list >( an_object ) )
        {
            scarab::param_ptr_t the_return( new scarab::param_array() );
            scarab::param_array& the_return_arr = the_return->as_array();
            for( auto an_item = an_object.begin(); an_item != an_object.end(); ++an_item )
            {
                the_return_arr.push_back( to_param( an_item ) );
            }
            return the_return;
        }
        else if( isinstance< dict >( an_object ) )
        {
            scarab::param_ptr_t the_return( new scarab::param_node() );
            scarab::param_node& the_return_arr = the_return->as_node();
            const dict& a_dict = static_cast< const dict& >( an_object );
            for( auto an_item = a_dict.begin(); an_item != a_dict.end(); ++an_item )
            {
                if( ! isinstance< str >(an_item->first) || ! isinstance< object >(an_item->second) )
                {
                    throw scarab::error() << "Cannot convert dict to param";
                }
                the_return_arr.add( static_cast< const str& >(an_item->first), to_param( static_cast< const object& >(an_item->second) ) );
            }
            return the_return;
        }
        throw scarab::error() << "Unknown python type cannot be converted to param";
    }

    pybind11::object to_python( const scarab::param& a_param )
    {
        if (a_param.is_null())
        {
            return pybind11::none();
        }
        else if (a_param.is_value())
        {
            const scarab::param_value& this_value = a_param.as_value();
            pybind11::object to_return;
            if (this_value.is_bool()) to_return =  pybind11::cast(this_value.as_bool());
            else if (this_value.is_uint()) to_return = pybind11::cast(this_value.as_uint());
            else if (this_value.is_int()) to_return = pybind11::cast(this_value.as_int());
            else if (this_value.is_double()) to_return = pybind11::cast(this_value.as_double());
            else if (this_value.is_string()) to_return = pybind11::cast(this_value.as_string());
            return to_return;
        }
        else if (a_param.is_array())
        {
            const scarab::param_array& this_array = a_param.as_array();
            pybind11::list to_return;
            for (scarab::param_array_const_iterator an_item=this_array.begin(); an_item != this_array.end(); ++an_item)
            {
                to_return.append( to_python( *an_item ) );
            }
            return to_return;
        }
        else if (a_param.is_node())
        {
            const scarab::param_node& this_node = a_param.as_node();
            pybind11::dict to_return;
            for (scarab::param_node_const_iterator an_item=this_node.begin(); an_item != this_node.end(); ++an_item)
            {
                //TODO how do I modify the contents of a pybind11::dict here... the following still fails
                to_return[ an_item.name().c_str() ] = to_python( *an_item );
            }
            return to_return;
        }
        throw scarab::error() << "Unknown param type cannot be converted to Python";
    }

    void export_param( pybind11::module& mod )
    {
        mod.def( "to_param", &to_param, "Convert native python types to a param structure." );

        // param
        pybind11::class_< scarab::param >( mod, "Param" )
            .def( pybind11::init< >() )
            .def( pybind11::init< scarab::param_value >() )

            .def( "__str__", &scarab::param::to_string )
            .def( "__call__", (scarab::param_value& (scarab::param::*)()) &scarab::param::operator(),
                    pybind11::return_value_policy::reference_internal )
            .def( "__getitem__", (scarab::param& (scarab::param::*)(unsigned)) &scarab::param::operator[],
                    pybind11::return_value_policy::reference_internal )
            .def( "__getitem__", (scarab::param& (scarab::param::*)(const std::string&)) &scarab::param::operator[],
                    pybind11::return_value_policy::reference_internal )
            //TODO: do we need __setitem__?

            .def( "is_null", &scarab::param::is_null )
            .def( "is_node", &scarab::param::is_node )
            .def( "is_array", &scarab::param::is_array )
            .def( "is_value", &scarab::param::is_value )

            .def( "as_array", (scarab::param_array& (scarab::param::*)()) &scarab::param::as_array,
                    pybind11::return_value_policy::reference_internal )
            .def( "as_node", (scarab::param_node& (scarab::param::*)()) &scarab::param::as_node,
                    pybind11::return_value_policy::reference_internal )
            .def( "as_value", (scarab::param_value& (scarab::param::*)()) &scarab::param::as_value,
                    pybind11::return_value_policy::reference_internal )

            .def( "to_python", &to_python )

            //TODO: has_subset()

            //TODO: get_value() in its various types

            //TODO: merge()

            ;
    }

} /* namespace scarab_pybind */
