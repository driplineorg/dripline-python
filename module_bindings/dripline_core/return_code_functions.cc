#include "indexed_factory.hh"
#include "return_codes.hh"

#include "return_code_functions.hh"

namespace dripline_pybind
{

    LOGGER( rcf, "return_code_functions" );

    std::list< unsigned > get_return_codes()
    {
        std::list< unsigned > return_codes;
        scarab::indexed_factory< unsigned, dripline::return_code >* the_factory = scarab::indexed_factory< unsigned, dripline::return_code >::get_instance();
        LDEBUG( rcf, "factory is at: " << the_factory );
        auto anIt = the_factory->begin();
        while (anIt != the_factory->end() )
        {
            return_codes.push_back( anIt->first );
            anIt++;
        }
        return_codes.push_back( 0 );
        return return_codes;
    }

} /* namespace dripline_pybind */
