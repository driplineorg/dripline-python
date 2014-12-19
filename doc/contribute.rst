Contribute
##########

Part of the motivation for moving to this incarnation of dripline is to make it easier for anyone to contribute.
We're trying to keep test coverage high, so a recommended test driven development workflow is (going to be soon, hopefully,) described below.

As always, `dripline is on github <github.com/project8/dripline>`_.
Branches are cheap, lets do more of those.
For more details, `this branching model <nvie.com/posts/a-successful-git-branching-model>`_ has served us very well to date.
In particular, please note that master is for tagged/release versions while develop is the latest working version.

TDD with Dripline
=================
Test driven development is a paradigm where having code that successfully passes some tests (called Unit Tests) is 
the decision metric for when a piece of code is up to standards.

Consider a very simple piece of code shown below:

.. code-block:: python

    class Adder(object):
        def __init__(self, x):
            self.x = x

        def add(self, y):
            return self.x - y

The above code has an obvious typo - we are subtracting in the ``add`` method where we clearly meant to add.  If we 
deployed this code in production, at some point it would break, and we would have to do some extensive debugging to 
figure out where.  This type of error is especially insidious as we would have to figure out not just that the 
arithmetic was bad, but also *where* the arithmetic went wrong.

If instead, we wrote the following piece of testing code *before we even implemented the class*, we would catch it
immediately:

.. code-block:: python

    def test_my_adder():
        for i in range(10):
            for j in range(10):
                an_adder = Adder(i)
                assert an_adder.add(j) == i + j

This is the crux of test driven development: we want to write tests that establish a contract for the code that we
haven't written yet.  We know how we *want* it to behave - and so we specify that as a test, and have a testing framework
run our tests for us.  Dripline uses the excellent `py.test <http://pytest.org>`_ for this, and an extensive number of tests
is in the ``test`` subdirectory of the dripline source tree.

Contributing with TDD
=====================
Think of the tests as a contract.  If you modify some code, and tests start failing, identify the source of the failure
and fix the code.  More than likely, if your contribution is self-contained, you won't break tests that belong to other
parts of the code - in other words, you are fulfilling the contract that is laid out by the tests.

To start, write down the contract in the tests directory as a file called ``test_whatever.py`` where whatever has something
to do with the code that you're writing.  Looking at e.g. ``test_factory.py`` may be a good place to get some inspiration,
as the code is extremely simple and highlights the basic idea:

.. code-block:: python

    import pytest
    from agilent34461a import Agilent34461a
    from factory import constructor_registry

    def test_reg_factory():
        c = constructor_registry['agilent34461a']
        assert c == Agilent34461a

This is extremely simple and verifies the core functionality of a piece of the dripline code.  Note that the test is
completely disinterested in the *internal* way in which the constructor_registry is built - all it cares about is that
the expected behavior is correct.

On that note, write tests that express the ideas you have about how your code ought to work.  If there are logical statements
or invariants that must be true for your code, write them as tests.  If you are writing a class that has some well-defined
API, ensure that it works as you expect it to!  If you have two methods on some object called ``set_x`` and ``get_x``, 
write a test to make sure that a call to ``get_x`` after ``set_x`` returns what you expect. 

Don't stop there
================
Once your tests pass, you've successfully fulfilled the contract - which is not the same as having the code that
you really want.  This is a great place to stop and refactor your code to be high quality, while still running tests
after changing things to verify that you haven't broken anything.  Doing things this way means that while you are
making your code pretty, the chances of making it wrong are dramatically reduced!

Adding Tests
============
If you suspect that some part of the dripline codebase may be fragile or break in some edge case, feel free to add a test
to try it!  It's much much simpler to write a single function than an entire program to test some aspect of the code.

Mocking
=======
Dripline is inherently network oriented, but when we are running tests we want to be isolated from connections to the
network.  To get around this and test the functionality of our code, it is necessary to *mock* certain functions and
classes so that the behavior of our code can be tested independently of communication with the outside world.

This may be a limitation in some respect, but note that you can mock a function in such a way that it will return whatever
you might expect from a remote host, and therefore preserve the logic of your program.

Mocking is a subject unto itself - see examples in ``test_node.py``, or read more extensively about the mocking capabilities
in py.test `here <http://pytest.org/latest/monkeypatch.html>`_
