..  MONK Testframework
    created on Mon Feb 11 2013
    (C) 2013, DResearch Fahrzeugelektronik GmbH

..  You can redistribute this file and/or modify it under the terms of the GNU
    General Public License as published by the Free Software Foundation; 
    either version 2 of the License, or (at your option) any later version

############
Contributing
############

.. toctree::
    :maxdepth: 2

As an open source project we are happy to work together with other enthusiastic
people in creating a better testing experience for all of us. In this chapter
you will learn everything you need to know to get involved in MONK development.


.. include:: undocumented.inc

*********************************
Communicating with the developers
*********************************

You can communicate with other MONK developers in one of the following ways:

 #. **The mailinglist**: You can ask questions at `project monk`_. You can also
     have a look at `the archives`_ to see old conversations.

 #. **The bug tracker**: If you have already a specific problem you want to
     work on, then you can create an Issue `here`_. It's also possible ot work
     with Github Pull Requests.

 #. **The Stammtisch Meeting**: If you happen to be in Berlin on a monday
     afternoon at 4.30pm, you might want to come to join our regular meeting
     with all topics around MONK:

    DResearch Fahrzeugelektronik GmbH
    Otto-Schmirgal-Str. 3, D-10319 Berlin, Germany

****************
Getting the Code
****************

MONK is hosted on `Github`_. You can `fork the repository`_ and then get your
results into the main repository with a pull request.

You can also simply clone it and do with it what you want::

    $ git clone https://github.com/DFE/MONK

***********************
The Development Process
***********************

If you want to make a change to MONK, the best way is to communicate your ideas
first with the other MONK developers. If others agree that the change makes
sense, only then should you start to put work into the solution. Otherwise you
might see, that your work will be done for nothing.

In case you don't work on a fork, which should only happen if you are a regular
member of the DFE group, then you can ignore the following steps that talk
about pull requests. In that case it is better to create an Issue from the
beginning and track your changes there in a feature branch. If you are only
able to work with pull requests, then remember that such a feature branch will
be automatically generated for your pull request.

 #. **start from the dev branch**: No matter how you want to start, you always
     need to make sure that your commits can work without problem from the
     current HEAD of the ``dev`` branch.

 #. **Create meaningful commits**: Commits should fulfill the requirements that
     are described in a later chapter. An important part is, that they should
     always contain only one meaningful change.

 #. **Create a Pull Request**: Follow the Github `Pull Request Guide`_.

 #. **Recieve Acknowledgements**: That a maintainer can accept your changes,
     you need to find 2 DFE developers first, who will acknowledge your
     changes. These 2 people should be mentioned in your commit message, as
     described later.

 #. **Get it merged**: If you have a pull request or Issue containing your
     problem, your solution, the commits and two Acked-Bys

If you need to change anything on your commits, e.g. add some ``Acked-by``
lines, then it is okay to ``rebase -i`` or ``commit --amend`` 
your changes on your feature branch or pull request, because nobody else should
work on the same feature branch anyway.

***************
Branching Model
***************

The MONK repository has different kinds of Branches:

 #. **The master branch**: Is the stable branch. It should only contain those
     project states that can be shipped to users.

 #. **The dev branch**: Contains the currently accepted features. Changes here
     might be more unstable and deviate from the documentation. Using MONK from
     here might break your code, but as a MONK developer you always need to
     start from the HEAD of this branch with your features and bug fixes.

 #. **Feature Branches**: Feature Branches are used by Members of
     `the DFE group`_ to work on bug fixes and new features.

 #. **Pull Requests**: Pull Requests are used by external MONK developers who
     want to get their changes merged into MONK.


**************************************
Acceptance Criteria for the Dev Branch
**************************************

``dev`` contains the latest changes that are considered to be working by their
creators and at least 2 reviewers. To continually ensure good quality of the
code, some requirements must be met for a commit to be allowed into ``dev``:

 * All commits belong to a Github Issue
 * The Issue contains an understandable description of the problem that enables
   reproduction if necessesary
 * The Issue contains an understandable and assessable description of the
   solution
 * All code changes are well documented, formatted according to the (not yet
   publicly available) coding standards and follow high quality standards even
   in areas that are not specifically mentioned here.
 * Code changes are unit tested with 100% statement coverage for the changes
   involved.
 * If necessary and possible: integration tests and documentation adapted
   accordingly.
 * 2 DFE team members acknowledged the solution's successful and complete
   implementation.

These requirements can be overruled only by 100% acceptance of all developers,
reviewers and both maintainers for a single Issue, if considered necessary.

Changes to this list of rules can only be achieved by acceptance at the
Stammtisch Meeting.

*****************************************
Acceptance Criteria for the Master Branch
*****************************************

The ``dev`` branch may be merged into the ``master`` branch whenever the
Stammtisch decides that MONK's current state warrants doing so.

*************
Commit Policy
*************

 * **KISS principle**: Commits should contain one meaningful change and
   that one change only. That doesn't mean you should only put changes in one
   file or one deletion/insertion into one commit, but all the changes should
   belong together to do one meaningful thing.

 * **All English**: As this documentation all relevant texts in MONK are
   written in English that non German mothertounge speakers can use it as well
   as we can.

 * **Summary Upfront**: The first line is for a short summary with not more
   then 50 characters. This line must be followed by an empty line

 * **Descriptive Content**: The following paragraphs are considered the long
   description of the problem as well as it's solution.

 * **72 chars per line**: Comment messages shouldn't exceed 72 characters,
   except longer URLs, cited text or otherwise unintelligible messages when
   split

 * **Signed-off-bys**: After the long description all developers involved in
   creating this commit should be mentioned with a seperated line beginning
   with ``Signed-off-by:``. these lines should include their name and email
   adress.

 * **Acked-bys**: Afterwards all people who checked the quality and spelling of
   the commits should be mentioned in the same fashion with ``Acked-by:``
   lines.


And finally a complete example that does everything correct::

    some_file: limit checks debugged

    There was a problem with the limits in this line. They excluded 0, which is
    still an acceptable value, which led to unexpected error messages in the
    GUI.

    The bug was fixed with changing the `>0` to `>=0`.

    For more details see Github Issue #312.

    Signed-off-by: Peter Parker <parker@dresearch-fe.de>
    Acked-by: Bruce Wayne <wayne@dresearch-fe.de>
    Acked-by: Clark Kent <kent@dresearch-fe.de>


********************************
Working with the MONK repository
********************************

There are some things to consider, when working in the MONK repositories. This
shall be covered in this section.

Configuring the Environment
===========================

In it's current state a :py:mod:`~monk_tf.devicetestcase.DeviceTestCase`
requires you to configure two serial connections for your device. One
connection to have access to a console and another to communicate with the
board controller. The serial ports for these connections have to be configured
in some environment variables, which you can find
:doc:`at the bottom of this page <api-docs>`.

Building and Installing from Source
===================================

Installing from source is quite simple. Just replace the ``<variabl>e`` parts
in the following commands and execute them::

    $ cd <your_monk_folder>
    $ python setup.py sbin #building
    $ pip uninstall monk_tf #delete current version, if already installed
    $ pip install dist/monk_tf-<version>.tar.gz #installing


Running the Tests
=================

MONK itself comes with a unittest suite, which checks if everything is working.
You can execute it like this::

    $ python tests/test_all.py


.. Links

.. _project monk: project-monk@dresearch-fe.de
.. _the archives: https://groups.google.com/a/dresearch-fe.de/forum/?fromgroups#!forum/project-monk
.. _here: https://github.com/DFE/MONK/issues
.. _Github: https://github.com/DFE/MONK
.. _fork the repository: https://help.github.com/articles/fork-a-repo
.. _Pull Request Guide: https://help.github.com/articles/using-pull-requests
.. _the DFE group: https://github.com/DFE
