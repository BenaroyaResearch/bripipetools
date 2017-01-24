.. _contribute-page:

************
Contributing
************

.. _contribute-style:

Nomenclature & style conventions
================================

All code, to the extent possible, should follow Python's PEP8 conventions.


.. _contribute-envs:

Anaconda and virtual environments
=================================

::

    source activate bripipetools


.. _contribute-git:

GitHub & TravisCI
=================

Version control for **bripipetools** is managed with **git** and all code lives on **GitHub** under the Benaroya Research account. The development model to date has more or less followed the "GitHub flow" — the master branch is assumed to be production-ready, and all new features and other changes are integrated by creating a new branch, opening a pull request, and merging the branch (assuming that all tests pass).

Cloning the repo:::

    git clone


Installing ``bripipetools`` (developer mode):::

    pip install -e .


Creating a new branch:::

    git checkout -b new-branch-name


Pushing a new branch to remote repo:::

    git push -u origin new-branch-name



Retrieving a new remote branch:

i.e., from a different location

::

    git fetch
    git checkout --track origin/new-branch-name


Cleaning up local repo after merging pull request:::

    git remote prune origin
    git branch -d new-branch-name

OR
::

    git branch | grep -v "master" | xargs git branch -D


-----

.. _contribute-test:

PyTest
======

Running tests
-------------

::

    py.test


::

    py.test tests/test_io.py


::

    py.test --cov-report term-missing


Basic test setup
----------------

example

Test organization
-----------------

Hierarchy
^^^^^^^^^

Test module per application package

Test class per application module/class

Test function/method per application function/method

GIVEN, WHEN, THEN
^^^^^^^^^^^^^^^^^

(example)


Parameterizing tests
--------------------

example

Using fixtures
--------------

example

-----

.. _contribute-docs:

Sphinx & ReadTheDocs
====================


.. _contribute-version:

Updating version
================

https://github.com/peritus/bumpversion

::

    bumpversion (patch|minor|major)


