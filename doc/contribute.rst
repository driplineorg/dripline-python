Contribute
##########


Branching
=========

Branches are cheap, lets do more of those.
For more details, `this branching model <nvie.com/posts/a-successful-git-branching-model>`_ has served us very well to date.
In particular, please note that master is for tagged/release versions while develop is the latest working version.
We name branches off of develop as ``feature/<description>`` and bug fixes off of master as ``hotfix/<description>`` so that they are sorted and easier to navigate.
You're welcome and encouraged to push your feature branch to github, we're not going to judge you for things that are incomplete and appreciate not loosing work if you move on or lose your laptop (at a minimum, we suggest pushing at the end of your work day).

Merging
=======

Merging follows the instruction from the branching section above in most cases, but there are a few additional notes:

  - If you'd like for someone to look over your changes before they are integrated, please push your branch and create a pull request
  - If you are new to dripline-python, we ask that you use a PR for anything other than a very minor change when contributing to develop
  - In the near term, we're planning to require PRs for all merges into the master branches when new releases are created

Coding Style
============

The internet is full of arguments over coding style which we're not really interested in getting into; in this repo we're going just go ahead and start with the following assumptions:

  - Regardless of what that style is, consistent styling makes code easier to read
  - If we follow what is used in the python community then that is more intuitive to new people
  - We're not robots and common sense can win out
  - doc strings can be special depending on how they are expected to be rendered (for example in the API docs section of this page)

Based on that we prefer the following:

  - Generally we try to follow `PEP-8 <https://www.python.org/dev/peps/pep-0008/>`_
  - The 80 column limit makes things harder to read more of then easier (displays have had more than 80 columns and editors have been wrapping text for some time now). Use your judgement on when forced line-wrapping is needed
  - When creating new classes which inherit from local classes, decorate them with ``@fancy_doc`` so that the class's docstring gets updated

    - The description of the class belongs in the class's doc string
    - The doc string for the ``__init__`` method should just include description of the kwargs for that class (the decorator will add kwargs from inherited classes)
