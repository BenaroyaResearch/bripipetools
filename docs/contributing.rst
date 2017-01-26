.. _contribute-page:

************
Contributing
************

.. _contribute-style:

Nomenclature & style conventions
================================

All code, to the extent possible, should follow Python's PEP8 conventions.

Variable names
--------------

Objects vs. documents

Python style
------------

PEP8

-----


.. _contribute-envs:

Anaconda and virtual environments
=================================

**Anaconda** is nominally a Python distribution, but also comes with the package/environment management tool ``conda``. You can install Anaconda by following the instructions on `this page <https://www.continuum.io/downloads>_`. Because ``bripipetools`` has largely been developed and tested in Python 2.7, the matching version of Anaconda is recommended.

Once installed, Anaconda can be used to create isolated virtual environments for development. To create a basic environment for Python, you can use the following command:::

    conda create -n bripipetools python

Alternatively, to start with an environment pre-configured with ``bripipetools`` dependencies, use:::

    conda env create -n bripipetools envirionment.yml

The environment can then be activated with this command:::

    source activate bripipetools

Any tools or libraries installed while the environment is accessed will only affect that environment — other system paths and the global Python installation will remain unaffected. Both ``conda install`` and ``pip install`` are acceptable ways to install resources within the environment.

To deactivate the conda envirionment, use this command:::

    source deactivate

-----


.. _contribute-git:

GitHub & TravisCI
=================

Version control for **bripipetools** is managed with **git** and all code lives on **GitHub** under the Benaroya Research account. The development model to date has more or less followed the "GitHub flow" — the master branch is assumed to be production-ready, and all new features and other changes are integrated by creating a new branch, opening a pull request, and merging the branch (assuming that all tests pass).

Below are some common steps/commands you can use when working with git.

Cloning the repo:::

    git clone


Installing ``bripipetools`` (developer mode):::

    pip install -e .


Creating a new branch:::

    git checkout -b new-branch-name


Pushing a new branch to remote repo:::

    git push -u origin new-branch-name



Retrieving a new remote branch (i.e., from a different location):::

    git fetch
    git checkout --track origin/new-branch-name


Cleaning up local repo after merging pull request:::

    git remote prune origin
    git branch -d new-branch-name

OR::

    git branch | grep -v "master" | xargs git branch -D


.. _contribute-test:

Issues
------

The best way to flag a problem, a desired feature, or some other proposed change to the code is creating a new issue on GitHub. This will not only get the attention of package maintaners, but also serves as a centralized to-do list. Even for primary developers of **bripipetools**, a recommended procedure would be:

1. Create a new issue describing what is wrong or missing and propose a strategy to update package code (optional: assign the issue to a package contributor)
2. Create a new branch to address the feature or change referenced in the issue
3. Make any changes, commit, open and merge pull request
4. Close the issue

-----


Testing with PyTest
===================

To ensure that any code updates or modifications do not break other parts of the application, it's recommended that any development be closely coupled with the writing and running of unit tests. The testing suite used by ``bripipetools`` is **PyTest**.

Running tests
-------------

Tests can be run at the command line as follows (assuming the current working directory is the ``bripipetools`` repo):::

    py.test


To run a specific test module:::

    py.test tests/test_io.py

Individual classes and methods in the test module can also be called as follows:::

    py.test tests/test_io.py::TestPicardMetricsFile::test_get_table


To view detailed information about which terms are covered in test targets, you can use the following option:::

    py.test --cov-report term-missing



Basic test setup
----------------

Here's a very basic example of how to set up a test.

::

    def test_to_camel_case():
        assert to_camel_case('snake_case_string') == 'camelCaseString'

The ``assert`` symbol is the only syntax used to perform the test (i.e., no boilerplate).

Test organization
-----------------

Tests are organized at two levels.

Hierarchy
^^^^^^^^^

* Test module per application package
* Test class per application module/class
* Test function/method per application function/method

GIVEN, WHEN, THEN
^^^^^^^^^^^^^^^^^

Most tests are logically organized into sections demarcated as "GIVEN", "WHEN", and "THEN".


Parameterizing tests
--------------------

A single block of test code can operate on multiple input scenarios through the ``pytest.mark.parameterize()`` function and decorator.


Using fixtures
--------------

Fixtures can be used to inject dependencies into a test.


-----


.. _contribute-docs:

Sphinx & ReadTheDocs
====================

Here's one of the better Sphinx/RST guides I've come across: `sphinx.rst <https://github.com/ContinuumIO/misc-docs-info/blob/master/source/directory/sphinx.rst#python>`_.

-----


.. _contribute-version:

Updating version
================

`bumpversion <https://github.com/peritus/bumpversion>_`

Usage::

    bumpversion (patch|minor|major)


