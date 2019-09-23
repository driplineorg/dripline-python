/*
 * dripline_python_version.hh
 *
 *  Created on: Sep 23, 2019
 *      Author: N.S. Oblath
 */

#ifndef DRIPLINE_PYTHON_VERSION_HH_
#define DRIPLINE_PYTHON_VERSION_HH_

#include "singleton.hh"

#include "scarab_version.hh"

#include <string>


namespace dripline_pybind
{

    class dl_python_version : public scarab::version_semantic
    {
        public:
            dl_python_version();
            ~dl_python_version();
    };

} // namespace dripline_pybind

#endif /* DRIPLINE_PYTHON_VERSION_HH_ */
