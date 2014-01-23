..  MONK Testframework
    created on Mon Feb 11 2013
    (C) 2013, DResearch Fahrzeugelektronik GmbH

..  You can redistribute this file and/or modify it under the terms of the GNU
    General Public License as published by the Free Software Foundation;
    either version 2 of the License, or (at your option) any later version

.. _chap-devel:

Development Process
===================

This page describes all the details about the development process. If you want
a short tutorial to start, have a look at :ref:`chap-contrib`.

Communicating with the Developers
---------------------------------

You can communicate with other :term:`MONK` developers in one of the following
ways:

 #. **The Mailing List**: You can ask questions at
    project-monk@dresearch-fe.de.  You can also have a look at `the archives`_
    to see old conversations.

 #. **The Bug Tracker**: If you have encountered a specific problem you want
    to work on, you can create an Issue `here`_. It is also possible to
    work via GitHub pull requests.

 #. **The Stammtisch Meeting**: If you happen to be in Berlin on any Tuesday
    afternoon at 2:30 pm, you are welcome to join our regular meeting on all
    topics concerning :term:`MONK` at:

    | DResearch Fahrzeugelektronik GmbH
    | Otto-Schmirgal-Str. 3
    | D-10319 Berlin
    | Germany

The Development Process
-----------------------

If you want to see your changes applied to :term:`MONK`, the best way is to
first communicate your ideas with the other :term:`MONK` developers. You should
only start development, if they agree the change makes sense. Otherwise, your
work might turn out to be a waste of time.

If you have write access to the repository (which is only supposed to happen if
you are a regular member of `the DFE group`_), you should simply fork, create
an Issue and track your changes in a feature branch.

If you do not have write access, you will have to use pull requests. Remember
that a feature branch will automatically be generated for your pull
request.

Step-by-step guide:

 #. **Start from the dev branch**: You always need to ensure your commits
    can be applied without problem on the current HEAD of the ``dev``
    branch.

 #. **Create meaningful commits**: Commits should adhere to the
    requirements described in `Commit Policy`_. An important point is,
    that they should always contain only one meaningful change.

 #. **Create a pull request**: Follow `Pull Request Guide`_ on GitHub.

 #. **Receive acknowledgements**: Before a maintainer may accept your changes,
    you will need to find one or more DFE developers to acknowledge them.
    These people should be mentioned within your commit message, as
    described later.

 #. **Get it merged**: If you have a pull request or Issue containing your
    problem, your solution, and the commits containing the two Acked-Bys,
    get one of the maintainers to merge it.

If you need to change anything on your commits, e.g., to add some ``Acked-by``
lines, it is okay to ``rebase -i`` or ``commit --amend`` your changes on
your feature branch or pull request as nobody else is supposed to work on
the same feature branch anyway.


Branching Model
---------------

There are five different kinds of branches in :term:`MONK`:

 #. **The Master Branch** is the stable branch. It should only contain
    project states that may be distributed to users.

 #. **The Dev Branch** contains all currently accepted features. Changes here
    might be more unstable than in the Master Branch and might not be properly
    documented. Using this branch might sometimes break your code, but as a
    :term:`MONK` developer you will always need to start implementing your
    features and bug fixes from the HEAD of this branch.

 #. **Feature Branches** are used by members of `the DFE group`_ to work on
    new features.

 #. **Bugfix Branches** are used by members of `the DFE group`_ to work on
    bug fixes.

 #. **Pull Requests** are used by external :term:`MONK` developers who want to
    get their changes merged into :term:`MONK`.


Acceptance Criteria For The Dev Branch
--------------------------------------

``dev`` contains the latest changes that are considered to be working by their
creators and at least one reviewer. To continually ensure good quality of the
code, some requirements must be met for a commit to be allowed into ``dev``:

 * All commits refer to an Issue on `GitHub`_.
 * The Issue contains an understandable description of the problem that enables
   reproduction, if necessesary.
 * The Issue contains an understandable and assessable description of the
   solution.
 * All code changes are well documented, formatted according to the coding
   standards, and follow high quality standards even in areas that are not
   specifically mentioned here.
 * Code changes are unit tested with 100% statement coverage for the changes
   involved.
 * If necessary and possible: integration tests and documentation have been
   adapted accordingly.
 * Two DFE team members have acknowledged the solution's successful and
   complete implementation.

These requirements can be overruled only by 100% acceptance of all developers,
reviewers, and both maintainers for a single Issue, if considered necessary.

Changes to this list of rules can only be achieved by acceptance at the
Stammtisch Meeting.

Acceptance Criteria for the Master Branch
-----------------------------------------

The ``dev`` branch may be merged into the ``master`` branch whenever the
Stammtisch decides that :term:`MONK`'s current state warrants doing so.

Commit Policy
-------------

All commits are are expected to adhere to the following requirements:

 * **KISS principle**: Commits should contain one meaningful change and
   that one change only. This does not mean you should only put changes in one
   file or one deletion/insertion into one commit, but that all of the changes
   should belong together to do one meaningful thing.

 * **All English**: All relevant texts in :term:`MONK` (like this
   documentation) are written in English so that non German speakers may use
   it. This, of course, applies to commits as well.

 * **Summary Upfront**: The first line contains a short summary with no more
   than 50 characters. This line must be followed by an empty line.

 * **Descriptive Content**: The following paragraphs contain the long
   description of the problem as well as its solution.

 * **72 characters per line**: Comment messages should not exceed 72
   characters per line, except for longer URLs, quotations or messages that
   would be unintelligible in some other way when split.

 * **Refer to an Issue on GitHub**: If you have not done so already within
   the description, this would be a good place to specify which Issue on
   GitHub your commit belongs to.

 * **Signed-off-bys**: After the long description all developers involved in
   creating this commit should be listed on separate lines beginning with
   ``Signed-off-by:``. These lines should include their names and email
   addresses.

 * **Acked-bys**: Afterwards all people who checked the quality of the
   commits should be mentioned in the same fashion with ``Acked-by:``
   lines.


Finally, a complete example doing everything right::

    some_file: limit checks debugged

    There was a problem with the limits in this line. They excluded 0,
    which is still an acceptable value. This led to unexpected error
    messages in the GUI.

    The bug was fixed by changing `>0` to `>=0`.

    For more details see GitHub Issue #312.

    Signed-off-by: Peter Parker <parker@dresearch-fe.de>
    Acked-by: Bruce Wayne <wayne@dresearch-fe.de>
    Acked-by: Clark Kent <kent@dresearch-fe.de>


.. Links

.. _git book: http://git-scm.com/book
.. _the Python website: http://www.python.org/getit/
.. _Installing Git: http://git-scm.com/book/en/Getting-Started-Installing-Git
.. _virtualenv Installation Guide: http://www.virtualenv.org/en/latest/#installation
.. _virtualenv documentation: http://www.virtualenv.org/en/latest/
.. _nosetests documentation: https://nose.readthedocs.org/en/latest/
.. _CI server: http://en.wikipedia.org/wiki/Continuous_integration
.. _Travis CI: https://travis-ci.org/DFE/MONK
.. _Sphinx: http://sphinx-doc.org/
.. _the corresponding Github page: https://github.com/DFE/MONK/blob/dev/doc/source/contributing.rst
.. _Devenv Issue: https://github.com/DFE/MONK/issues/36
.. _tut comment: https://github.com/DFE/MONK/issues/36#issuecomment-18195272
.. _the archives: https://groups.google.com/a/dresearch-fe.de/forum/?fromgroups#!forum/project-monk
.. _here: https://github.com/DFE/MONK/issues
.. _GitHub: https://github.com/DFE/MONK
.. _fork the repository: https://help.github.com/articles/fork-a-repo
.. _Pull Request Guide: https://help.github.com/articles/using-pull-requests
.. _the DFE group: https://github.com/DFE
