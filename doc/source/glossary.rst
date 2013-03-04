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
