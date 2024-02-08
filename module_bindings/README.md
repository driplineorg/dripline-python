# Library installation
The library file that contains the Python package can be installed in the Python site-packages directory, or 
in the lib install directory.
- To install in site-packages (as defined by `${Python3_SITELIB}`), set `INSTALL_DLPYBIND_IN_SITELIB` to `TRUE`
- To install in the lib install directory (as defined by `${CMAKE_INSTALL_LIBDIR}`), set `INSTALL_DLPYBIND_IN_SITELIB` to `FALSE`

# General python binding guides
- The python module is defined in a single source file, it runs exporter functions defined in header files which correspond one-to-one with source files in dripline-python; they have names ending in `_pybind.hh`.
- When needed, trampoline classes and extra functions in support of bindings should be defined in their own source and header files as needed.
- It is preferrable to try to achieve pythonic interfaces for bound classes; this means naming arguments and providing default values where possible and including doc strings.

# Items list convention
In python, if a module has an attribute named `__all__`, then that lists (as strings) the names of the objects to be imported when doing `from <module> import *`.
Our pattern is to use that style of import in `__init__.py` files to bring classes and other implementations into the namespace of a package, and so this is required for bound C++ as well.
In order to handle this in a consistent way, the following convention is established:
1. The main source fill which calls `PYBIND11_MODULE` constructs an `std::list< std::string >`, which is added as the `__all__` attribute of the module.
2. Every exporter function, generally one per header, which takes the above should return an `std::list< std::string >` of the names of the objects which have been added.
3. The main source file will collect these (using `std::list<>::splice`) to construct the module's `__all__`.

Note: This pattern mirrors the python source file pattern, where each file initializes an empty `__all__` list object, then appends object names to it as those objects are defined in the source.


# `mv_referrable` function bindings (used for complex types)
The `mv_referrable` macro (from project8's scarab repo) expands into 2 functions:
- `[return_type]& [function_name]()`
- `const [return_type]& [function_name]() const`
We will use only the first one as the get, and the second in a lambda for the set in a python property
The following is an exmaple of binding a `mv_referrable`:

```
.def_property( "routing_key", (std::string& (dripline::message::*)()) &dripline::message::routing_key,
    [](dripline::message& an_obj, const std::string& a_routing_key )
            { an_obj.routing_key() = a_routing_key; } )
```

# `mv_accessible` function bindings (used for simple types)
The `mv_accessible` macro (also from project8's scarab repo) is for simpler types and should be bound using the pattern found [here](https://pybind11.readthedocs.io/en/master/classes.html#instance-and-static-fields)
which results in the following binding:

```
.def_property( "name", &some::class::get_name, &some::class::set_name)
```

# Other quick references to common problems

When there appears to be a problem with bindings returning a non-trivial type, refer to [here](https://pybind11.readthedocs.io/en/stable/advanced/functions.html?highlight=policy#return-value-policies)

For issues with class holders involving shared or unique pointers, refer to [here](https://pybind11.readthedocs.io/en/stable/advanced/smart_ptrs.html?highlight=shared#smart-pointers)

For binding protected member functions, refer to [here](https://pybind11.readthedocs.io/en/stable/advanced/classes.html#binding-protected-member-functions)

For binding functions and giving them default values, refer to [here](https://pybind11.readthedocs.io/en/stable/advanced/functions.html#default-arguments-revisited)

When creating bindings in which assigning default values does not work, refer to [here](https://pybind11.readthedocs.io/en/stable/classes.html#binding-lambda-functions)
Also if a function requires an object to use it, it might be useful to use a lambda function

