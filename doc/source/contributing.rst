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

Our project lives from your contributions. That's why we took a lot of effort
to make contributing to MONK as easy as possible. Following the guide on this
page leads you to your first steps developing with and for MONK.

********
Tutorial
********

Prerequisites
=============

MONK is written in **Python 2.7**, which means it is mostly self
containing and able to work on any operating system. Not all OS dependencies
can be obvious, though. This means, that in some places you might have to
investigate a solution by yourself. Feel free to drop us a line, though. Maybe
we already faced your problem before or might include your solution as your
first contribution!

Most MONK developers work on Ubuntu, Suse and Fedora systems. If you have one
of those systems, your chances are very high that you can follow this guide
without any problems. This document itself is written on a **Ubuntu 13.04**
machine and all examples here are tested on that platform.

On most Linux distributions Python 2.7 should already be installed, so you
have nothing to do in that regard. To test it, open a Terminal and look if
that works without an error message::

    $ python
    Python 2.7.4 (default, Apr 19 2013, 18:28:01)
    [GCC 4.7.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> print "hi"
    hi
    >>> exit()

If it worked, than you already have Python and are ready to go. If not, you
might find information on `the Python website`_.

Another requirement is the version control system used for MONK. It's called
**git** and you can find a lot of information about it in the `git book`_. To
follow this guide it's not necessary to know everything about git, though.
Don't worry about it. The only thing you should have a look at is the
`Installing Git`_ chapter.

Then you will need 2 development packages. One is **python-dev** (might be
called *python-devel*) and the other one
is **libssh-2-1-dev** (sometimes called *libssh2-devel*). They are necessary
to build the Python package *libssh2*, which can be installed for you
automatically, if you have the 2 *\*-dev* packages installed. Those are
packages created by your operating system vendor and you should use his
resources to get them. On Ubuntu 13.04 you can do the following::

    $ sudo apt-get install python-dev libssh-2-1-dev

You will also need a Python tool, that helps with generalizing
development environments. It's called **virtualenv**. If your operating system
doesn't come with a prebuilt virtualenv, you can follow the `virtualenv
Installation Guide`_.

And of course you will need MONK's source code. If you have installed *git* on
your system, you can go to your preferred development folder and write the
following line::

    $ git clone https://github.com/DFE/MONK

This will create a new folder in that location and will download the source
code inside.

Now you are ready to start developing for MONK. Great!

Starting The Environment
========================

Now we want to discuss how to start our environment. It means an additional
step before and after your editing, but it comes with a lot of advantages.
The tool that helps us here is *virtualenv* and what it does is creating a
defined local environment. It resets standard variables like ``PATH`` and
creates additional folders at the position of your *virtualenv*. Using it
gives the following advantages:

 * All developers using the same *virtualenv* initialization work in pretty
   much the same environment.
 * You separate your development environment from your system, which might be
   good, if you normally use another python version or another set of python
   packages.
 * A lot of tools and services expect to run python code in a *virtualenv*. So
   it's always good to be prepared for it.


Working with *virtualenv* requires the following steps:

  #. Create a *virtualenv* (only once)
  #. Initialize the *virtualenv* (every time before you work)
  #. Install the requirements (once in the beginning, and updated when changed)
  #. Develop, test and do whatever you need to do.
  #. Deactivate the *virtualenv* (every time after you are finished with your
     work)

To create the virtualenv ``cd`` into your MONK folder, and then run the
following command::

    MONK$ virtualenv .

Now you run ``git status``. You will see there are a lot of new folders which
are not part of the MONK repository. Those were created by *virtualenv* and
normally you don't need to touch them directly.

Every time before you start working on something you should run this command::

    MONK$ . bin/activate
    (MONK)MONK$

If the activation was successful, then you should see the name of the folder
inside braces before your prompt. If you don't see it, then please refer to the
`virtualenv documentation`_.

The next step you need to do is run the requirements. If you want to develop,
you can install the *requirements-tests.txt* and if you want to develop you can
install the *requirements-develop.txt*. Because it doesn't hurt, we just
install both now::

    (MONK)MONK$ pip install -r requirements-test.txt
    (MONK)MONK$ pip install -r requirements-develop.txt

Remember that this step only needs to be done once in the beginning and when
those file got updated. If there are no changes it doesn't hurt to call them
again, but it also shouldn't change anything.
Now you can start working. In a later chapter we will look at things we can do
here.

Now that you've tested that everything is okay, you want to install MONK inside
of your *virtualenv* in a way, that makes it possible to test it and to develop
it. This is achieved with the following command::

    (MONK)MONK$ python setup.py develop

After you are finished, you deactivate the *virtualenv* with this command::

    (MONK)MONK$ deactivate
    MONK$

You see, that the name in brackets before the prompt is gone and you are back
in the normal mode.

Now you know everything you need to start working with *virtualenv*. Awesome!


Running The Testsuite
=====================

.. note::

    You need to install the requirements-test.txt file and execute
    ``python setup.py develop`` before you can go on with this chapter! See the
    previous chapter for a setup.

By now we have prepared our system, we retrieved the source code for MONK, and
we saw how to use *virtualenv* to start our development environment. As a first
example of doing stuff, we want to run MONK's unit test suite. It will also
show us, if everything is installed correctly.

To run the test suite go into the *virtualenv* and then run the setup command
for **nosetests**. *nosetests* is a tool that finds and runs testsuites while
also collecting coverage data. This tool will be automatically installed while
running the setup command. You only need to worry about it in case of errors or
when you start to write unit tests yourself. In that case refer to the
`nosetests documentation`_.

The command::

    MONK$ . bin/activate
    (MONK)MONK$ python setup.py nosetests

This command will install all required python packages locally into the folder.
Read the output carefully. In general you should see successful attempts to
download and install some packages, then a ``DEBUG`` output, were *nose*
searches the path for all kinds of tests, then tests and their success,
followed by the coverage data and a short summary that should be successful.
If you experience errors in this step it's save to contact
our mailing list (project-monk@dresearch-fe.de)!

To check if it is working, you can go into one file that is being tested and
change something. Because we can be sure that there is a test for
``monk_tf/serial_conn.py``, we will change that::

    (MONK)MONK$ vim monk_tf/serial_conn.py #or any editor of your choice

In that file add a line with ``raise Exception("Hello Error!")`` in the
constructor (the :py:meth:`~monk_tf.serial_conn.SerialConn.__init__` method).
If you run the tests again with ``python setup.py nosetests`` from the
project's root folder (*MONK* in our example), the tests with
:py:class:`~monk_tf.serial_conn.SerialConn` should all fail with that
exception.

After you are finished, you can remove the Exception and don't forget to
*deactivate* your environment::

    (MONK)MONK$ deactivate

The interesting point is, that you can now test on the go while developing. Not
much different from what an IDE would offer you. But in contrast to the IDE you
also know that you have an equal environment to other developers, users and
your `CI server`_, in our case `Travis CI`_.


Reading the Documentation
=========================

The MONK documentation is written in `Sphinx`_. Sphinx is a set of tools, which
compiles documents in the :term:`restructuredText <reST>` markup language to
different formats like HTML and PDF. :term:`reST` is a language that is both
written for compilers to parse, as well as for humans to read. That makes
reading :term:`.rst <reST>` directly in your editor possible. Text editors
like VIM will even highlight the :term:`reST` format for you. So the simplest
way to read the documentation will be directly in the source tree::

    (MONK)MONK$ cd doc/source
    #read this page's source file:
    (MONK)MONK$ vim contributing.rst

Another way to read the docs, is on `the corresponding Github page`_, but make
sure that you are at the right commit. The advantages of the website are that
you don't need any environment for reading it, Github already parses it to HTML
for you and you can even edit the text there. For changing the documentation
that might be a solid way to handle it, although we didn't test it until now!

The more advanced way is to build the docs yourself to PDF or HTML. This will
be explained in the next section. The advantages here are that you read all the
warnings and error messages and have full control over every part of your
documentation. If you want to be a successful MONK developer this is definitely
the way to go. It is not the easiest, though. But we trust you can handle it!

Building the Documentation
==========================

As always the first step is to go into your MONK repository and activate the
*virtualenv*::

    $ cd <MONK>
    MONK$ . bin/activate
    (MONK)MONK$

Then you go into the doc folder::

    (MONK)MONK$ cd doc
    (MONK)doc$

When you look into that folder you see that there is a *Makefile* and that
contains tasks for everything you could want to do. In general you just want
the html docs. In that case you call::

    (MONK)doc$ make html

If you want to build everything and decide later what to use, then::

    (MONK)doc$ make

Keep in mind that building everything requires some latex related system
libraries. Until now we have no comprehensive list about those and fall back to
simply install the Lyx Latex editor, which automatically installs all required
packages (and some more)::

    (MONK)doc$ deactivate
    doc$ sudo apt-get install lyx
    doc$ . ../bin/activate
    (MONK)doc$ make

We seldomly use PDF by now, that's why nobody got to improve that part. So if
you use that heavily, then we would appreciate your commits there!

The output you see then begins by trying to delete old folders that might still
be lying around. Then *Sphinx* is started and the output you see is *Sphinx*
going through it's compilation process, followed by the output from *latexpdf*
a tool to generate PDFs from text files.

If everything ran successfully, you should find the following documents, which
can be opened with a browser and a pdf reader respectively::

    MONK/doc/build/html/index.html
    MONK/doc/build/latex/MONK.pdf

For problems with building the HTML you should refer to the `Sphinx`_
Documentation. For problems with building the PDF we can’t help you. Sorry!
But we wish you a great deal of luck! :)

In the end, don't forget to deactivate your *virtualenv*::

    (MONK)doc$ deactivate
    doc$


Change Example: Creation Of This Tutorial
=========================================

As a last point of this tutorial I want to discuss how the changes were made to
put this tutorial here in this place. This part is just for reading. I hope you
understand that it's not possible to have any specific change in the project,
that can be always go through the whole MONK development process each time
someone wants to go through the tutorial. We just hope that after reading this
you will have the confidence to go ahead and do something yourself with MONK.
If you hit any road blocks on the way, don't hesitate to ask for our help!

History Lesson
--------------

This tutorial was developed, because one of our developers felt, that the
previous version of this document wasn't very convincing to new users. It was
basically a list of details about the development process, with too much
information and too little guidance. So when the time was right and enough
changes to the development process were made, this tutorial was created for new
comers, to get an easier step into MONK and open source development. Although
there is probably still a lot to be done better, we hope we at least succeeded
in convincing you to work with us on MONK.


The Preparation
---------------

The problem was discovered by one coworker with the Github shorthand erikb85.
When he noticed the problem, he started `an Issue <Devenv Issue>`_ on our
developer platform Github. In that he described the problem. Because in this
case he already knew the solution to the problem, he desribed that as well. In
most cases the solution won't be clear. Then that part of the Issue description
stays empty until a solution is found.

After that he fetched the newest version of MONK from Github. Because he
already has a development environment, it wasn't necessary to clone MONK::

    #go to the MONK folder
    $ cd MONK
    #make sure to be on the right branch
    MONK$ git checkout dev
    #pull updates from Github
    MONK$ git pull --rebase

Then he created a feature branch for his new commits and added it to the
*Notes* section in the Issue::

    MONK$ git checkout -b f-docs-devenv

Now he started the development environment and went to the documentation
folder::

    MONK$ . bin/activate
    (MONK)MONK$ cd doc
    (MONK)doc$

Then he started to edit the *contributing.rst* and built the html documentation
to check his results::

    (MONK)doc$ vim source/contributing.rst
    (MONK)doc$ make html
    ...
    (MONK)doc$ chromium-browser build/html/contributing.html
    # repeat until happy or time runs out

When he left work, he committed his changes in form of a WIP commit, always
mentioning the Github Issue with ``#36``. This way Github always knew were the
commit belongs to and could list it in the Issue::

    (MONK)doc$ git add source/contributing.rst
    (MONK)doc$ git commit -s
    #commit message:
    WIP: contributing.rst: Rewrite for development env

    See Github Issue #36.

    Signed-off-by: Erik Bernoth <erik.bernoth@gmail.com>
    #end of commit message
    #be careful with the following command, because it influences the internal
    #structure of your git repository as well as GitHub's
    (MONK)doc$ git push -f origin f-docs-devenv

Now the most up-to-date version is always online and all commits show in the
GitHub Issue. Some major decisions are also written as comments to the Issue.
An example is `the comment <tut comment>`_, which discusses changes to the
topic issue, which seemed meaningful at some point while working on solving
it. This is also a place for reviewers, interested users and other developers
to discuss their ideas about the problem.

After this tutorial was finished, it got the label *reviewable* and other
developers took a look into it. A reviewer will checkout the same branch (not a
commit specifically) and look at the results. If code was changed he will look
what happened and if the code still works as expected, if unit tests are there,
if they pass and if the coding style guide was followed. If he is happy, he
will write a comment with a simple ``ACK`` inside. Sometimes it gets more
complicated and he will communicate with the developer directly. The result
will be as in this case more commits by the reviewers or some changes by the
developer himself. If 2 reviewers give an ``ACK`` in comments or directly to
the developer he or a maintainer will go through the commits and add a line for
each reviewer to the commit message, saying that this commit was checked by
whom::

    TODO: add Acked-by line according to Issues #36 reviewers. If you are a
    reviewer and read this, add an Acked-by example with your name here,
    please.

Then a maintainer will close the issue and merge the feature branch with the
``dev`` branch. Now the Issue is solved.

As you might have noticed, the last steps were explained more broadly. They
require a deeper understanding of git and at the point were you get there, a
MONK developer will probably already help you, anyway.

Final Words
===========

Okay, that closes the tutorial. Now you have learned all the steps in the
development process and seen one example of how it was applied. You should know
why and how to use virtualenv, git, Github and MONK. Some more detailed
descriptions follow underneath and in the next chapters. We hope, you could
learn something and have a good time developing on MONK.

Thanks for reading to this point!

******************
Reference Material
******************

Communicating with the Developers
=================================

You can communicate with other MONK developers in one of the following ways:

 #. **the Mailing List**: You can ask questions at 
    project-monk@dresearch-fe.de.  You can also have a look at `the archives`_
    to see old conversations.

 #. **the Bug Tracker**: If you have encountered a specific problem you want
    to work on, you can create an Issue `here`_. It is also possible to
    work with Github Pull Requests.

 #. **the Stammtisch Meeting**: If you happen to be in Berlin on any Tuesday
    afternoon at 2:30 pm, you are welcome to join our regular meeting on all
    topics concerning MONK at:

    | DResearch Fahrzeugelektronik GmbH
    | Otto-Schmirgal-Str. 3
    | D-10319 Berlin
    | Germany

The Development Process
=======================

If you want to see your changes applied to MONK, the best way is to first
communicate your ideas with the other MONK developers. You should only start
development, if they agree the change makes sense. Otherwise, your work might
turn out to be a waste of time.

If you have write access to the repository (which is only supposed to happen
if you are a regular member of `the DFE group`_), you should simply fork, create
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

 #. **Receive acknowledgements**: Before a maintainer may accept your
    changes, you will need to find two DFE developers to acknowledge them.
    These two people should be mentioned within your commit message, as
    described later.

 #. **Get it merged**: If you have a pull request or Issue containing your
    problem, your solution, and the commits containing the two Acked-Bys,
    get one of the maintainers to merge it.

If you need to change anything on your commits, e.g. to add some ``Acked-by``
lines, it is okay to ``rebase -i`` or ``commit --amend`` your changes on
your feature branch or pull request as nobody else is supposed to work on
the same feature branch anyway.


Branching Model
===============

There are four different kinds of branches in MONK:

 #. **the Master Branch** is the stable branch. It should only contain
    project states that may be distributed to users.

 #. **the Dev Branch** contains all currently accepted features. Changes here
    might be more unstable than in the Master Branch and might not be
    properly documented. Using this branch might sometimes break your code,
    but as a MONK developer you will always need to start implementing your
    features and bug fixes from the HEAD of this branch.

 #. **Feature Branches** are used by members of `the DFE group`_ to work on
    bug fixes and new features.

 #. **Pull Requests** are used by external MONK developers who want to get
    their changes merged into MONK.


Acceptance Criteria for the Dev Branch
======================================

``dev`` contains the latest changes that are considered to be working by their
creators and at least two reviewers. To continually ensure good quality of the
code, some requirements must be met for a commit to be allowed into ``dev``:

 * All commits refer to an Issue on `GitHub`_.
 * The Issue contains an understandable description of the problem that enables
   reproduction, if necessesary.
 * The Issue contains an understandable and assessable description of the
   solution.
 * All code changes are well documented, formatted according to the coding
   standards and follow high quality standards even in areas that are not
   specifically mentioned here.
 * Code changes are unit tested with 100% statement coverage for the changes
   involved.
 * If necessary and possible: integration tests and documentation adapted
   accordingly.
 * Two DFE team members have acknowledged the solution's successful and
   complete implementation.

These requirements can be overruled only by 100% acceptance of all developers,
reviewers and both maintainers for a single Issue, if considered necessary.

Changes to this list of rules can only be achieved by acceptance at the
Stammtisch Meeting.

Acceptance Criteria for the Master Branch
=========================================

The ``dev`` branch may be merged into the ``master`` branch whenever the
Stammtisch decides that MONK's current state warrants doing so.

Commit Policy
=============

All commits are are expected to adhere to the following requirements:
    
 * **KISS principle**: Commits should contain one meaningful change and
   that one change only. This does not mean you should only put changes in one
   file or one deletion/insertion into one commit, but that all of the changes
   should belong together to do one meaningful thing.

 * **All English**: All relevant texts in MONK (like this documentation) are
   written in English so that non German speakers may use it. This, of course,
   applies to commits as well.

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
   creating this commit should on seperate lines beginning with
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
