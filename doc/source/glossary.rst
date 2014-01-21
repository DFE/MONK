.. MONK Testframework
   You can adapt this file completely to your liking.

########
Glossary
########

.. glossary::

    API
        Short for Application Programming Interface. The interface a piece of
        software provides to other software to use for programming purposes.

    cross-compiling
        The act of compiling software on one architecture, i.e., a personal
        computer, for another architecture, i.e., an :term:`embedded system`.

    cross-testing
        The act of testing a :term:`system under test` on one device (the
        :term:`test host`) while
        executing it on another (the :term:`target device`).

    DFE
        DResearch Fahrzeugelektronik GmbH. The company which develops
        :term:`MONK`.

    embedded system
        A computer highly adapted to a specific usecase, often used inside
        cars, trains, airplanes, etc.

    extended INI
        A text format based on the :term:`INI` format, that also allows
        nesting.

    fixture
        Short for :term:`test fixture`.

    fixture file
        A file that contains data in :term:`extended INI` format. It will be
        read by a :py:class:`~monk_tf.fixture.Fixture` object.

    INI
        A traditional text file format consisting of sections that contain
        key-value pairs of data. Used often for configuration files and
        description of relational data.

    MONK
        This is the framework you are reading the documentaion from, right now!

    nose
        A Python tool to run :term:`unit tests<unit test>`. See its PyPi page:
        `nose <https://pypi.python.org/pypi/nose/1.3.0>`_.

    open source
        Software that can be used and developed without the need to pay license
        fees first. The usage here is broader than the combination of the
        defintion of Free Software by the Free Software Foundation and the
        defintion of Open Source by the Open Source Initiative.

    PIP
        the package manager for Python packages. Often used together with
        :term:`virtualenv` to create independently managed projects.

    regression test
        A test that is created for the purpose of being run many times, e.g.,
        every night or after every change to a system.

    reST
        reST is the short form of *restructuredText*, which is a markup format
        for text files.

    shell command
        A command that can be executed by a shell, typcially bash. Shell
        commands are sent when interacting with a :term:`target device`
        remotely via serial connection or ssh.

    SUT
        An abbreviation of :term:`system under test`.

    system under test
        The system of hardware and software that should be run in a test. It
        can be very small like a function or really big, like a network of
        servers. It completely depends on the :term:`test case`. It is good
        practice to call the system under test :term:`SUT` in
        :term:`test scripts<test scripting>`.

    target device
        A device that you interact with remotely to test it. In our case it is
        a :term:`embedded system` that is configured to do a specific task
        which will be tested in our :term:`test cases<test case>`. A
        :term:`MONK` test always requires two computers. A target device and a
        :term:`test host`.

    test case
        A test case is a set of :term:`test fixture`, actions, verification
        steps, and clean up steps that run one specific test.

    test fixture
        The :term:`system under test` and its surrounding environment in
        specificially defined state (as far as it is possible).

    test framework
        A well maintained :term:`test scripting` project consists of two parts.
        One part are the *test scripts* themselves and the other part is a
        *test framework* of helper classes and functions that should help in
        clarifying the test code and take care of some of the complexity.

    test host
        A computer that runs your :term:`test suites<test suite>` for you. It
        does not contain the :term:`system under test` though. This would be
        the :term:`target device`. A :term:`MONK` test always requires both a
        :term:`target device` and a test host.

    test scripting
        writing tests in a programming language. Other ways of testing software
        could be record&replay or manual testing.

    test suite
        A set of :term:`test cases<test case>` that is run together.

    unit test
        In general a unit test is the lowest level of testing, verifying a
        specific unit of a system for one detail of functionality. In
        :term:`open source` development the term is often used for all kinds of
        tests that are written with a unit test framework. This also includes
        integration tests, :term:`regression tests<regression test>`, etc. In
        this documentation the second definition is used.

    virtualenv
        A tool that creates independent Python environments in which Python
        packages can be installed, removed or updated depending on manual
        usage of the package manager :term:`pip`, and via *requirements.txt*
        files.


.. Links

.. _Wiki markup: http://en.wikipedia.org/wiki/Help:Wiki_markup
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _reST website: http://docutils.sourceforge.net/rst.html
