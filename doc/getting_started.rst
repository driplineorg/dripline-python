Getting Started
===============

Requirements
------------

Libraries
*********
The only required librares are `pika <pika.readthedocs.org>`_ and `PyYAML <pyyaml.org>`_.
To build this documentation, you also need `sphinx <http://sphinx-doc.org/>`_ and `sphinx_rtd_theme <https://github.com/snide/sphinx_rtd_theme>`_.
All three can be obtained through `pip <http://pip.readthedocs.org/en/latest/installing.html>`_.

Operating System & Python
*************************
The development of dripline is being done on OS X and various linux systems.
While running on windows or other operating systems may be possible, the author's make no promise or offer of support.
Similarly, the expected versions of python are 2.7.3 and >= 3.3.0.
We will try to keep the codebase compatible with both, but use of older versions is untested and not guaranteed to work.

Prepare an Environment
----------------------

The recommended usage is with a `virtual environment <virtualenv.readthedocs.org/en/latest>`_ and the `ipython <ipython.org>`_ interpreter.
Assuming you have virtualenv installed (most likely available in the package manager for your system) it is relatively simple to get everything going.
For the complete experience, you would run the following three commands::

$ virtualenv path/to/virt_environments/dripline
$ source path/to/virt_environments/dripline/bin/activate
$ pip install ipython pika PyYAML sphinx sphinx_rtd_theme

Note that sphinx is only required if you want to (re)build this documentation and sphinx_rtd_theme is purely cosmetic.
Similarly, ipython is nice for the user but does not change available dripline features.

