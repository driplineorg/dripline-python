##########
Contribute
##########


Branching
=========

Branches are cheap, lets do more of those.
For more details, `this branching model <nvie.com/posts/a-successful-git-branching-model>`_ has served us very well to date.
In particular, please note that master is for tagged/release versions while develop is the latest working version.
We name branches off of develop as ``feature/<description>`` and bug fixes off of master as ``hotfix/<description>`` so that they are sorted and easier to navigate.
In the hopefullly infrequent event of a major version change to the dripline standard, we will follow a parallel structure of branches for the new version prefixed with ``dl<N>`` (where ``<N>`` is replaced with the major version number of dripline).

Anyone is welcome to fork the repo and pass back changes via pull request.
Frequent contributors may request membership in the github organization, which will allow pushing feature and hotfix branches directly to the driplineorg repo.


Merging
=======

Merging follows the instruction from the branching section above in most cases, but there are a few additional notes:

  - With the default travis-ci config, if the name of your branch ends in ``\build``, then when you push it will trigger travis-ci tasks
  - Anyone may offer contributions by forking and opening a PR, org members can push branches directly but are still expected to use PRs when contributing to the ``develop`` or ``master`` branches.


Coding Style
============

The internet is full of arguments over coding style which we're not really interested in getting into; in this repo we're going just go ahead and start with the following assumptions:

  - Regardless of what that style is, consistent styling makes code easier to read
  - If we follow what is used in the python community then that is more intuitive to new people
  - We're not robots and common sense can win out
  - doc strings can be special, depending on how they are expected to be rendered (for example in the API docs section of this page)

Based on that we prefer/stress the following:

  - Generally we try to follow `PEP-8 <https://www.python.org/dev/peps/pep-0008/>`_
  - We're using sphinx with ``sphinx-apidoc`` and have the `sphinx.ext.napolean extension<https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_. Google style docstrings are preferred, but proper parsing is most important.
  - The 80 column limit makes things harder to read as often as easier (displays have had more than 80 columns and editors have been wrapping text for some time now). Use your judgement on when forced line-wrapping is needed
  - For multi-line python data structures which support it, place a comma after the final element and the closing symbol on its own line, that way any element may be easily commented out.
  - Use unix-style line endings and soft tabs in all files (other than the documentation Makefile)


Testing
============

Since we reuse some cpp code here using Pybind, we have provided some unit tests to make sure such classes and methods work properly. These tests are contained in the ``/tests`` folder and can be run using PyTest. An overview can be found `there <http://doc.pytest.org/en/5.3.5/goodpractices.html/>`_.

How to run the tests:
  - After installing the package, either navigate to the folder and run all tests within it using ``python -m pytest``, or specify the path to the test to be run using ``python -m pytest tests/to/be/run/test_something.py``.
  - To disable the caching, use ``PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider``.

How to add a new test:
  - Name your file with ``test_`` prefix, followed by the name of the class to be tested.
  - Within the file, write ``test`` prefixed methods to be run. Ideally, one such method is supposed to test only one case. To keep unit tests simple and independent of each other, test classes are not suggested.
