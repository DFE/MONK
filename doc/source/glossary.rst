.. MONK Testframework
   You can adapt this file completely to your liking.

########
Glossary
########

.. glossary::

    cross-compiling
        The act of compiling software on one architecture, i.e. a personal
        computer, for another architecture, i.e. an embedded system.

    embedded system
        A computer highly adapted to a specific usecase, often used inside
        cars, trains, airplane and the likes.

    reST
        reST is the short form of *restructuredText*, which is a markup format
        for text files. Much like `Wiki markup`_ or `Markdown`_ it is a
        language with 2 goals: easily readable and writeable source code, as
        well as a logical structure understandable by a compiler program.
        Writing reST source files is often not too different from simply
        writing a text into a normal txt file. But with the logical structure
        together it can be compiled to formatted HTML or PDF. Writing in those
        markup languages is also considered easier then writing HTML directly.
        reST itself was created for documenting the Python core libraries.
        Today it developed to the quasi standard for documenting all kinds of
        Python projects and some projects in other languages use it as well.
        See the `reST website`_ for more details.

    target vs development system
        Embedded systems are highly specialised for one task and that task
        alone. Because these tasks are unrelated to software development most
        of the time, the software for these embedded systems needs to be
        developed on a separated system, which is often a normal personal
        computer. The system the software is developed **on** is called the
        *development system* and the system the software is developed **for**
        is called the *target system*.

    test framework
        A well maintained :term:`test scripting` project consists of two parts.
        One part are the *test scripts* themselves and the other part is a
        *test framework* of helper classes and functions that should help in
        clarifying the test code and take care of some of the complexity.

    test scripting
        writing tests in a programming language. Other ways of testing software
        could be record&replay or manual testing.

    Usecase
        Contains all the default configurations of a general branch of
        activities with the framework. Every time you use MONK, you will also
        apply a Usecase, if you know about it or not. The most important and
        simplest Usecase is the :py:mod:`monk_tf.SingleUsecase`.


.. Links

.. _Wiki markup: http://en.wikipedia.org/wiki/Help:Wiki_markup
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _reST website: http://docutils.sourceforge.net/rst.html
