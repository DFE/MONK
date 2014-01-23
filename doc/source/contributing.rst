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
:term:`MONK`. If you want to get into the details look at the next section:
:ref:`chap-devel`.

.. _contrib-pre:

Prerequisites
-------------

:term:`MONK` is written in **Python 2.7**, which means it is mostly self
contained and able to work on any operating system. Not all OS dependencies
can be obvious, though. This means, that in some places you might have to
investigate a solution by yourself. Feel free to drop us a line, though. Maybe
we already faced your problem before or might include your solution as your
first contribution!

Most :term:`MONK` developers work on Ubuntu, Suse and Fedora systems. If you
have one of those systems, chances are that you will be able to follow this
guide without any problems. This document itself is written on a **Ubuntu
13.04** machine and all examples have been tested on that platform.

On most Linux distributions Python 2.7 should already be installed, so you
have nothing to do in that regard. To test it, open a terminal and look if
that works without an error message::

    $ python
    Python 2.7.4 (default, Apr 19 2013, 18:28:01)
    [GCC 4.7.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> print "hi"
    hi
    >>> exit()

If it worked, then you already have Python and are ready to go. If not, you
might find information on how to get it on `the Python website`_.

Another requirement is the version control system used for :term:`MONK`. It is
called **git** and you can find a lot of information abou tit in the `git
book`_. To follow this guide it is not necessary to know everything about git,
though.  Do not worry about it. The only thing you should have a look at is the
`Installing Git`_ chapter.

Then you will need two development packages. One is **python-dev** (might be
called *python-devel* on some systems) and the other one
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

And, of course, you will need :term:`MONK's<MONK>` source code. If you have 
installed *git* on your system, you can go to your preferred development 
folder and do the following::

    $ git clone https://github.com/DFE/MONK

This will create a new folder in that location and will download the source
code inside.

You are now ready to start developing for :term:`MONK`. Great!

.. _contrib-startenv:

Starting The Environment
------------------------

We now want to discuss how to start our virtual environment. It requires an 
additional step before and after your editing, but it comes with a lot of 
advantages. The tool that helps us here is :term:`virtualenv`, which creates a
defined local environment. It resets standard variables like ``PATH`` and
creates additional folders at the position of your :term:`virtualenv`. Using it
provides the following advantages:

 * All developers using the same :term:`virtualenv` initialization work in
   pretty much the same environment.

 * You separate your development environment from your system, which might be
   a good idea, if you normally use another python version or another set of 
   python packages.

 * A lot of tools and services expect to run python code in a
   :term:`virtualenv`. So it is always good to be prepared for it.


Working with :term:`virtualenv` requires the following steps:

  #. Create a :term:`virtualenv` (only once).
  #. Initialize the :term:`virtualenv` (every time before you work).
  #. Install the requirements (once in the beginning, and updated when changed).
  #. Develop, test and do whatever you need to do.
  #. Deactivate the :term:`virtualenv` (every time after you are finished with
     your work).

To create the :term:`virtualenv` ``cd`` into your :term:`MONK` folder, and then
run the following command::

    MONK$ virtualenv .

Run ``git status`` now. You will see there are a lot of new folders which
are not part of the :term:`MONK` repository. Those were created by
:term:`virtualenv` and normally you do not need to touch them directly.

Every time before you start working on something you should run this command::

    MONK$ . bin/activate
    (MONK)MONK$

If the activation was successful, you should see the name of the folder
within braces in front of your prompt. If you do not see it, then please 
refer to the `virtualenv documentation`_.

The next step you need to do is install the requirements. If you want to test,
you can install *requirements-tests.txt* and if you want to develop you can
install *requirements-develop.txt*. Because it does not hurt, we will just
install both now::

    (MONK)MONK$ pip install -r requirements-test.txt
    (MONK)MONK$ pip install -r requirements-develop.txt

Remember that this step only needs to be done once in the beginning and whenever
these file got updated. If there are no changes it does not hurt to call them
again as it should not change anything.
Now you can start working. In a later chapter we will look at things we can do
here.

Now that you have tested that everything is okay, you want to install
:term:`MONK` inside of your :term:`virtualenv` in a way, that makes it possible
to test and to develop it. This is achieved with the following command::

    (MONK)MONK$ python setup.py develop

After you are finished, you deactivate :term:`virtualenv` with this command::

    (MONK)MONK$ deactivate
    MONK$

As you can see, the name in braces in front of the prompt is gone and you are 
back in normal mode.

Now you know everything you need to start working with :term:`virtualenv`.
Awesome!


.. _contrib-runtests:

Running The Testsuite
---------------------

.. note::

    You need to install the requirements-test.txt file and execute
    ``python setup.py develop`` before you can go on with this part! See
    :ref:`contrib-startenv` for a setup.

By now we have prepared our system, retrieved the source code for
:term:`MONK`, and we have seen how to use :term:`virtualenv` to start our 
development environment. As a first example of doing stuff, we want to run
:term:`MONK's<MONK>` :term:`test suite`. This will also demonstrate if 
everything has been installed correctly.

To run the test suite go into the :term:`virtualenv` and then run the setup
command for **nosetests**. :term:`Nose` is a tool that finds and runs
test suites while also collecting coverage data. This tool should have been 
installed automatically while running MONK's setup. You only need to worry a
bout it in case of errors or when you start to write unit tests yourself. 
In that case refer to the `nosetests documentation`_.

To run *nose* use::

    MONK$ . bin/activate
    (MONK)MONK$ python setup.py nosetests

This command will install all required python packages locally into the folder.
Read the output carefully. In general you should see successful attempts to
download and install some packages, then a ``DEBUG`` output, where *nose*
searches the path for all kinds of tests, then tests and their success,
followed by the coverage data and a short summary that should be successful.
If you experience errors in this step you might consider contacting
our mailing list (project-monk@dresearch-fe.de)!

To check if it is working, you can go into one file that is being tested and
change something. Because we can be sure that there is a test for
``monk_tf/serial_conn.py``, we will use it as an example::

    (MONK)MONK$ vim monk_tf/conn.py #or any editor of your choice

In that file add a line with ``raise Exception("Hello Error!")`` in the
constructor of :py:class:`~monk_tf.conn.SerialConnection` (the
:py:meth:`~monk_tf.conn.SerialConnection.__init__` method).  If you run the
tests again with ``python setup.py nosetests`` from the project's root folder
(:term:`MONK` in our example), the tests with :py:mod:`~monk_tf.conn` should
all fail with that exception.

After you are finished, you can remove the exception and do not forget to
*deactivate* your environment::

    (MONK)MONK$ deactivate

The interesting point is, that you can now test on the go while developing, much
like an IDE would offer you. In contrast to the IDE, however, you
know that you have the same environment as other developers, users, and
your `CI server`_, in our case `Travis CI`_.


.. _contrib-read:

Reading the Documentation
-------------------------

The :term:`MONK` documentation is written in `Sphinx`_. Sphinx is a set of
tools, which compiles documents in the :term:`reStructuredText <reST>` markup
language to different formats like HTML and PDF. :term:`reST` is a language
that is both written for compilers to parse and humans to read.
That makes reading :term:`.rst <reST>` directly in your editor possible. Text
editors like Vim will even highlight the :term:`reST` format for you. So the
simplest way to read the documentation will be directly in the source tree::

    (MONK)MONK$ cd doc/source
    #read this page's source file:
    (MONK)MONK$ vim contributing.rst

Another way to read the docs, is on `the corresponding GitHub page`_, but make
sure that you are at the right commit. The advantages of the website are that
you do not need any environment for reading it, GitHub already parses it to
HTML for you and you can even edit the text there. This might be a suitable way 
to handle changes in the documentation, although we have not tested
this so far.

The more advanced way is to build the documentation's PDF or HTML files yourself. 
This will be explained in the next section. The advantages offered by this
approach are that you may read all the warnings and error messages and have 
full control over every part of your documentation. If you want to be a 
successful :term:`MONK` developer this is definitely the way to go. 
It is not the easiest, but we trust you can handle it!

.. _contrib-build:

Building the Documentation
--------------------------

As always the first step is to go into your :term:`MONK` repository and
activate :term:`virtualenv`::

    $ cd <MONK>
    MONK$ . bin/activate
    (MONK)MONK$

Change into the doc folder::

    (MONK)MONK$ cd doc
    (MONK)doc$

When you look into that folder you can see that there is a *Makefile* that
contains tasks for everything you might want to do. In general you just want
the html docs. In that case you call::

    (MONK)doc$ make html

If you want to build everything and decide what to use later on, then::

    (MONK)doc$ make

Keep in mind that building everything requires some LaTeX related system
libraries. Until now we have no complete list of those and instead
install the LyX LaTeX editor, which automatically installs all required
packages (and some more)::

    (MONK)doc$ deactivate
    doc$ sudo apt-get install lyx
    doc$ . ../bin/activate
    (MONK)doc$ make

We only rarely use the PDF files, which is why nobody got around to 
improving that part. So if you prefer using PDF files, then we would appreciate 
your commits there!

The output you see then begins by trying to delete old folders that might still
be lying around. Then *Sphinx* is started and the output you see is produced by
*Sphinx* going through its compilation process, followed by the output from 
*latexpdf* a tool to generate PDF files from text files.

If everything ran successfully, you should find the following documents, which
can be opened with a browser or a PDF reader, respectively::

    MONK/doc/build/html/index.html
    MONK/doc/build/latex/MONK.pdf

For problems with building the HTML you should refer to the 
`Sphinx Documentation`_. For problems with building the PDF we cannot help you. 
Sorry! But we wish you a great deal of luck! :)

When finished, do not forget to deactivate your :term:`virtualenv`::

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

This tutorial was developed because one of our developers felt, that the
previous version of this document was not very helpful for new users. It was
basically a list of details about the development process, with too much
information and too little guidance. So when the time was right and enough
changes to the development process had been made, this tutorial was created 
to help newcomers to get involved in :term:`MONK` and :term:`open source`
development. Although there is probably still a lot of room for improvement, 
we hope we at least succeeded in convincing you to work with us on :term:`MONK`.


.. _contrib-example-prep:

The Preparation
^^^^^^^^^^^^^^^

The problem was discovered by erikb85 (GitHub username).
When he noticed the problem, he started `an issue <Devenv Issue>`_ on our
developer platform GitHub. In this issue he described the problem. Because in 
this case he already knew the solution to the problem, he described that 
as well. In most cases the solution will not be clear. Then that part of 
the issue description stays empty until a solution is found.

Afterwards he fetched the newest version of :term:`MONK` from GitHub. Because
he already had a development environment, it was not necessary to clone
:term:`MONK`::

    #go to the MONK folder
    $ cd MONK
    #make sure to be on the right branch
    MONK$ git checkout dev
    #pull updates from Github
    MONK$ git pull --rebase

He then created a feature branch for his new commits::

    MONK$ git checkout -b f-docs-devenv

He added the name of this branch to the *Notes* section of the issue.
    
Now he started the development environment and changed to the documentation
folder::

    MONK$ . bin/activate
    (MONK)MONK$ cd doc
    (MONK)doc$

Then he started to edit *contributing.rst* and built the html documentation
to check his results::

    (MONK)doc$ vim source/contributing.rst
    (MONK)doc$ make html
    ...
    (MONK)doc$ chromium-browser build/html/contributing.html
    # repeat until happy or time runs out

Whenever he left work, he committed his changes in form of a WIP commit, always
mentioning the GitHub Issue with ``#36``. This way GitHub always knew which
issue the commits belonged to and could list them accordingly::

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

This ensures the most up-to-date version is always available at GitHub and all 
commits are listed in the GitHub issue. Some major decisions are also added as 
comments to the issue. One example is `the comment <tut comment>`_, which 
discusses changes to the issue topic, which seemed meaningful at some point 
while working on solving it. The comments also are a place for reviewers, 
interested users, and other developers to discuss their ideas about the problem.

After this tutorial was finished, it was the labelled *reviewable* and other
developers took a closer look at it. A reviewer will checkout the same branch 
(not a specific commit) and evaluate the results. If code was changed he will 
check what exactly was done and if the code still works as expected, if unit 
tests are there, if they succeed, and if the coding style guide was followed. 
If he is happy, he will add a comment containing a simple ``ACK``. Sometimes 
it gets more complicated and he will communicate with the developer directly. 
This will result in more commits by the reviewers or some changes by the
developer himself. If two reviewers give an ``ACK`` in comments or directly to
the developer he or a maintainer will amend all commits by adding a line for
each reviewer to the commit message, stating that this commit was checked by
them::

    TODO: add Acked-by line according to Issues #36 reviewers. If you are a
    reviewer and read this, add an Acked-by example with your name here,
    please.

Then a maintainer will close the issue and merge the feature branch with the
``dev`` branch, thereby solving the issue.

As you might have noticed, the last steps were explained more broadly. They
require a deeper understanding of git and by that point, a :term:`MONK` 
developer will probably already help you, anyway.

.. _contrib-final:

Final Words
-----------

Okay, that closes the tutorial. Now you have learned all the steps in the
development process and seen one example of how they were applied. You should 
know why and how to use :term:`virtualenv`, git, GitHhub and :term:`MONK`. 
The next chapters contain more detailed descriptions. We hope, you were able to
learn something and wish you a good time developing on :term:`MONK`.

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
.. _Sphinx Documentation: http://sphinx-doc.org/
.. _the corresponding GitHub page: https://github.com/DFE/MONK/blob/dev/doc/source/contributing.rst
.. _Devenv Issue: https://github.com/DFE/MONK/issues/36
.. _tut comment: https://github.com/DFE/MONK/issues/36#issuecomment-18195272
.. _the archives: https://groups.google.com/a/dresearch-fe.de/forum/?fromgroups#!forum/project-monk
.. _here: https://github.com/DFE/MONK/issues
.. _GitHub: https://github.com/DFE/MONK
.. _fork the repository: https://help.github.com/articles/fork-a-repo
.. _Pull Request Guide: https://help.github.com/articles/using-pull-requests
.. _the DFE group: https://github.com/DFE
