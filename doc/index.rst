.. dripline-python documentation primary file

===========================================
Welcome to Dripline-python's documentation!
===========================================

Dripline-python builds on :doc:`dripline-cpp <dripline-cpp:index>` to provide useful
implementations for assembly of a dripline mesh. The package is split into three components (each a
namespace): ``core``, for extending ``dripline-cpp`` with a pythonic interface and adding the most basic
and generic features; ``implementations``, for ready to use classes that enable generic support for various
devices, resources, and behaviors; and ``extensions``, for enabling plugins via namespace packages.
There is also a commandline tool, ``dl-serve``, which enables ``YAML``-based configurations to define
the components in a running service.

Table of contents
=================

.. toctree::
   :maxdepth: 2

   getting_started
   extending
   dl_serve
   API Documentation <apidoc/modules>
   contribute

.. toctree::
   :caption: Links:

   Dripline Docs <https://driplineorggithubio.readthedocs.io/>
   Guides and Walkthroughs <https://controls-guide.readthedocs.io/>
   Protocol <https://dripline.readthedocs.io/>
   C++ Implementation <https://dripline-cpp.readthedocs.io/>
   Python Implementation <https://dripline-python.readthedocs.io/>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
