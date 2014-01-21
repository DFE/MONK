..  MONK Testframework
    created on Mon Feb 11 2013
    (C) 2013, DResearch Fahrzeugelektronik GmbH

..  You can redistribute this file and/or modify it under the terms of the GNU
    General Public License as published by the Free Software Foundation; 
    either version 2 of the License, or (at your option) any later version

.. _chap-contrib:

Contributing
============

.. toctree::
    :maxdepth: 2

Our project lives from your contributions. That is why we took a lot of effort
to make contributing to :term:`MONK` as easy as possible. Following the guide
on this page leads you to your first steps developing with and for
:term:`MONK`. If you want to get into the details look that the next section:
:ref:`chap-devel`.

.. _contrib-pre:

Prerequisites
-------------

:term:`MONK` is written in **Python 2.7**, which means it is mostly self
containing and able to work on any operating system. Not all OS dependencies
can be obvious, though. This means, that in some places you might have to
investigate a solution by yourself. Feel free to drop us a line, though. Maybe
we already faced your problem before or might include your solution as your
first contribution!

Most :term:`MONK` developers work on Ubuntu, Suse and Fedora systems. If you
have one of those systems, your chances are very high that you can follow this
guide without any problems. This document itself is written on a **Ubuntu
13.04** machine and all examples here are tested on that platform.

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

Another requirement is the version control system used for :term:`MONK`. It is
called **git** and you can find a lot of information about it in the `git
book`_. To follow this guide it is not necessary to know everything about git,
though.  Do not worry about it. The only thing you should have a look at is the
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
development environments. It is called :term:`virtualenv`. If your operating
system does not come with a prebuilt :term:`virtualenv`, you can follow the
`virtualenv Installation Guide`_.

And of course you will need :term:`MONK's<MONK>` source code. If you have installed
*git* on your system, you can go to your preferred development folder and write
the following line::

    $ git clone https://github.com/DFE/MONK

This will create a new folder in that location and will download the source
code inside.

Now you are ready to start developing for :term:`MONK`. Great!

.. _contrib-startenv:

Starting The Environment
------------------------

Now we want to discuss how to start our environment. It means an additional
step before and after your editing, but it comes with a lot of advantages.  The
tool that helps us here is :term:`virtualenv` and what it does is creating a
defined local environment. It resets standard variables like ``PATH`` and
creates additional folders at the position of your :term:`virtualenv`. Using it
gives the following advantages:

 * All developers using the same :term:`virtualenv` initialization work in
   pretty much the same environment.

 * You separate your development environment from your system, which might be
   good, if you normally use another python version or another set of python
   packages.

 * A lot of tools and services expect to run python code in a
   :term:`virtualenv`. So it is always good to be prepared for it.


Working with :term:`virtualenv` requires the following steps:

  #. Create a :term:`virtualenv` (only once)
  #. Initialize the :term:`virtualenv` (every time before you work)
  #. Install the requirements (once in the beginning, and updated when changed)
  #. Develop, test and do whatever you need to do.
  #. Deactivate the :term:`virtualenv` (every time after you are finished with
     your work)

To create the :term:`virtualenv` ``cd`` into your :term:`MONK` folder, and then
run the following command::

    MONK$ virtualenv .

Now you run ``git status``. You will see there are a lot of new folders which
are not part of the :term:`MONK` repository. Those were created by
:term:`virtualenv` and normally you do not need to touch them directly.

Every time before you start working on something you should run this command::

    MONK$ . bin/activate
    (MONK)MONK$

If the activation was successful, then you should see the name of the folder
inside braces before your prompt. If you do not see it, then please refer to
the `virtualenv documentation`_.

The next step you need to do is run the requirements. If you want to develop,
you can install the *requirements-tests.txt* and if you want to develop you can
install the *requirements-develop.txt*. Because it does not hurt, we just
install both now::

    (MONK)MONK$ pip install -r requirements-test.txt
    (MONK)MONK$ pip install -r requirements-develop.txt

Remember that this step only needs to be done once in the beginning and when
those file got updated. If there are no changes it does not hurt to call them
again, but it also should not change anything.
Now you can start working. In a later chapter we will look at things we can do
here.

Now that you have tested that everything is okay, you want to install
:term:`MONK` inside of your :term:`virtualenv` in a way, that makes it possible
to test it and to develop it. This is achieved with the following command::

    (MONK)MONK$ python setup.py develop

After you are finished, you deactivate the :term:`virtualenv` with this command::

    (MONK)MONK$ deactivate
    MONK$

You see, that the name in brackets before the prompt is gone and you are back
in the normal mode.

Now you know everything you need to start working with :term:`virtualenv`.
Awesome!


.. _contrib-runtests:

Running The Testsuite
---------------------

.. note::

    You need to install the requirements-test.txt file and execute
    ``python setup.py develop`` before you can go on with this part! See
    :ref:`contrib-startenv` for a setup.

By now we have prepared our system, we retrieved the source code for
:term:`MONK`, and we saw how to use :term:`virtualenv` to start our development
environment. As a first example of doing stuff, we want to run
:term:`MONK's<MONK>` :term:`test suite`. It will also show us, if everything is
installed correctly.

To run the test suite go into the :term:`virtualenv` and then run the setup
command for **nosetests**. :term:`Nose` is a tool that finds and runs
testsuites while also collecting coverage data. This tool will be automatically
installed while running the setup command. You only need to worry about it in
case of errors or when you start to write unit tests yourself. In that case
refer to the `nosetests documentation`_.

The command::

    MONK$ . bin/activate
    (MONK)MONK$ python setup.py nosetests

This command will install all required python packages locally into the folder.
Read the output carefully. In general you should see successful attempts to
download and install some packages, then a ``DEBUG`` output, were *nose*
searches the path for all kinds of tests, then tests and their success,
followed by the coverage data and a short summary that should be successful.
If you experience errors in this step it is save to contact
our mailing list (project-monk@dresearch-fe.de)!

To check if it is working, you can go into one file that is being tested and
change something. Because we can be sure that there is a test for
``monk_tf/serial_conn.py``, we will change that::

    (MONK)MONK$ vim monk_tf/conn.py #or any editor of your choice

In that file add a line with ``raise Exception("Hello Error!")`` in the
constructor of :py:class:`~monk_tf.conn.SerialConnection` (the
:py:meth:`~monk_tf.conn.SerialConnection.__init__` method).  If you run the
tests again with ``python setup.py nosetests`` from the project's root folder
(:term:`MONK` in our example), the tests with :py:mod:`~monk_tf.conn` should
all fail with that exception.

After you are finished, you can remove the Exception and do not forget to
*deactivate* your environment::

    (MONK)MONK$ deactivate

The interesting point is, that you can now test on the go while developing. Not
much different from what an IDE would offer you. But in contrast to the IDE you
also know that you have an equal environment to other developers, users and
your `CI server`_, in our case `Travis CI`_.


.. _contrib-read:

Reading the Documentation
-------------------------

The :term:`MONK` documentation is written in `Sphinx`_. Sphinx is a set of
tools, which compiles documents in the :term:`restructuredText <reST>` markup
language to different formats like HTML and PDF. :term:`reST` is a language
that is both written for compilers to parse, as well as for humans to read.
That makes reading :term:`.rst <reST>` directly in your editor possible. Text
editors like VIM will even highlight the :term:`reST` format for you. So the
simplest way to read the documentation will be directly in the source tree::

    (MONK)MONK$ cd doc/source
    #read this page's source file:
    (MONK)MONK$ vim contributing.rst

Another way to read the docs, is on `the corresponding Github page`_, but make
sure that you are at the right commit. The advantages of the website are that
you do not need any environment for reading it, Github already parses it to
HTML for you and you can even edit the text there. For changing the
documentation that might be a solid way to handle it, although we did not test
it until now!

The more advanced way is to build the docs yourself to PDF or HTML. This will
be explained in the next section. The advantages here are that you read all the
warnings and error messages and have full control over every part of your
documentation. If you want to be a successful :term:`MONK` developer this is
definitely the way to go. It is not the easiest, though. But we trust you can
handle it!

.. _contrib-build:

Building the Documentation
--------------------------

As always the first step is to go into your :term:`MONK` repository and
activate the :term:`virtualenv`::

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

We seldomly use PDF by now, that is why nobody got to improve that part. So if
you use that heavily, then we would appreciate your commits there!

The output you see then begins by trying to delete old folders that might still
be lying around. Then *Sphinx* is started and the output you see is *Sphinx*
going through its compilation process, followed by the output from *latexpdf* a
tool to generate PDFs from text files.

If everything ran successfully, you should find the following documents, which
can be opened with a browser and a pdf reader respectively::

    MONK/doc/build/html/index.html
    MONK/doc/build/latex/MONK.pdf

For problems with building the HTML you should refer to the `Sphinx`_
Documentation. For problems with building the PDF we can’t help you. Sorry!
But we wish you a great deal of luck! :)

In the end, do not forget to deactivate your :term:`virtualenv`::

    (MONK)doc$ deactivate
    doc$


.. _contrib-example:

Change Example: Creation Of This Tutorial
-----------------------------------------

As a last point of this tutorial I want to discuss how the changes were made to
put this tutorial here in this place. This part is just for reading. I hope you
understand that it is not possible to have any specific change in the project,
that can be always go through the whole :term:`MONK`
:ref:`development process<chap-devel>` each time someone wants to go through
the tutorial. We just hope that after reading this you will have the confidence
to go ahead and do something yourself with :term:`MONK`.  If you hit any road
blocks on the way, do not hesitate to ask for our help!

.. _contrib-history:

History Lesson
^^^^^^^^^^^^^^

This tutorial was developed, because one of our developers felt, that the
previous version of this document was not very convincing to new users. It was
basically a list of details about the development process, with too much
information and too little guidance. So when the time was right and enough
changes to the development process were made, this tutorial was created for new
comers, to get an easier step into :term:`MONK` and :term:`open source`
development. Although there is probably still a lot to be done better, we hope
we at least succeeded in convincing you to work with us on :term:`MONK`.


.. _contrib-example-prep:

The Preparation
^^^^^^^^^^^^^^^

The problem was discovered by one coworker with the Github shorthand erikb85.
When he noticed the problem, he started `an Issue <Devenv Issue>`_ on our
developer platform Github. In that he described the problem. Because in this
case he already knew the solution to the problem, he described that as well. In
most cases the solution will not be clear. Then that part of the Issue
description stays empty until a solution is found.

After that he fetched the newest version of :term:`MONK` from Github. Because
he already has a development environment, it was not necessary to clone
:term:`MONK`::

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
:term:`MONK` developer will probably already help you, anyway.

.. _contrib-final:

Final Words
-----------

Okay, that closes the tutorial. Now you have learned all the steps in the
development process and seen one example of how it was applied. You should know
why and how to use :term:`virtualenv`, git, Github and :term:`MONK`. Some more
detailed descriptions follow in the next chapters. We hope, you could learn
something and have a good time developing on :term:`MONK`.

Thanks for reading to this point!

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
