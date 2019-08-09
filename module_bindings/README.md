# mv_referrable function bindings (used for complex types)
mv_referrable expands into 2 functions
- ``[return_type]& [function_name]()``
- ``const [return_type]& [function_name]() const``

The following is an exmaple of binding a mv_referrable

```.def_property( "routing_key", (std::string& (dripline::message::*)()) &dripline::message::routing_key,
    [](dripline::message& an_obj, const std::string& a_routing_key )
            { an_obj.routing_key() = a_routing_key; } )```

# mv_accessible function bindings (used for simple types)

mv_accessible functions should be bound using the pattern found here
- https://pybind11.readthedocs.io/en/master/classes.html#instance-and-static-fields
which results in the following binding

``.def_property( "name", &some::class::get_name, &some::class::set_name)``

# Other quick references to common problems

When there appears to be a problem with bindings returning a non-trivial type, refer to here
https://pybind11.readthedocs.io/en/stable/advanced/functions.html?highlight=policy#return-value-policies

For issues with class holders involving shared or unique pointers, refer to here
https://pybind11.readthedocs.io/en/stable/advanced/smart_ptrs.html?highlight=shared#smart-pointers

For binding protected member functions, refer to here
https://pybind11.readthedocs.io/en/stable/advanced/classes.html#binding-protected-member-functions

For binding functions and giving them default values, refer to here
https://pybind11.readthedocs.io/en/stable/advanced/functions.html#default-arguments-revisited

When creating bindings in which assigning default values does not work, refer to here
https://pybind11.readthedocs.io/en/stable/classes.html#binding-lambda-functions
Also if a function requires an object to use it, it might be useful to use a lambda function

