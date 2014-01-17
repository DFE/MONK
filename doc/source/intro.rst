..  MONK Testframework
    created on Mon Feb 11 2013
    (C) 2013, DResearch Fahrzeugelektronik GmbH

..  You can redistribute this file and/or modify it under the terms of the GNU
    General Public License as published by the Free Software Foundation; 
    either version 2 of the License, or (at your option) any later version

.. _chap-intro:

Getting Started
===============

.. _intro-problem:

What Is The Problem?
--------------------

This framework is for developers of :term:`embedded systems<embedded system>`
like ourselves. We found that testing our systems manually via serial shell or
ssh was not very convinient in the long run, because for new devices new tests
needed to be repeated again and again. We also knew from other software
development applications that many :term:`open source` projects use
:term:`unit tests<unit test>` for writing :term:`test suites<test suite>` for
their :term:`regression tests<regression test>`. These tests are written in
test methods or functions that can be executed by tools like :term:`nose` to
generate a standardized output that states which tests could succeed and which
failed. Writing :term:`unit tests<unit test>` directly for testing embedded
systems is not so easy, though. The reason is that the code
which runs on your :term:`embedded system` (which we will call
:term:`target device` from now on) can not be accessed by the test code
directly, because the test code runs on another computer that collects the test
results, which we will call :term:`test host`. Therefore you need to implement
additional layers of communication between both :term:`test host` and
:term:`target device`, which is hard, complicated and error prone.

Thus the problem about writing :term:`regression<regression test>`
:term:`test suites<test suite>` is that the matter gets complicated because the
communication of two devices is involved.

.. _intro-solution:

Our Solution: MONK
------------------

:term:`MONK` comes in handy here, because it is a framework that abstracts
communication between two devices. It is expected to be run on the
:term:`test host` inside :term:`test suites<test suite>` and is able to
abstract communication channels or full :term:`target devices<target device>`
into single objects that manage most of the communication for you. You define
what commands you want to execute remotely and :term:`MONK` takes care of that.
A *hello world test* with :term:`MONK` and :term:`nose` might look like this::

    import nose.tools as nt
    import monk_tf.harness as mh

    def test_hi():
        """ send an echo and receive a hello
        """
        # set up
        h = mh.Harness("target_device_login.cfg")
        expected_response = "hello"
        send_msg = "echo \"{}\"".format(expected_response)
        # execute
        response = h.devs[0].cmd(send_msg)
        # assert - verify response is as expected
        nt.eq_(expected_response, response)
        # tear down
        h.tear_down()

The code example contains a complete python file that should be executable with
the :term:`nose` test tooling. In the first two lines :term:`MONK` and
:term:`nose` are imported and given shorter names for faster access. Then a
:term:`test case` is defined. The method's documentation contains a short line
that explains what the test does. In verbose mode :term:`nose` will use this
string for a human readable explanation of what is tested. Afterwards follow
four steps: set up, execute, assert, tear down. These are the common four steps
of a :term:`test case`. In the set up phase a
:py:class:`~monk_tf.harness.Harness` object is created and given the name of a
file. This file contains the information necessary to communicate with the
:term:`target device`, e.g., the information to access a serial connection and
login credentials. An example content will be discussed later. The
:py:class:`~monk_tf.harness.Harness` object will read this file and create
:term:`MONK` objects for you based on the configuration. This helps to separate
the information necessary to communicate with a :term:`device<target device>`
from the information that is important for a :term:`test case`. As you see in
the example it is not necessary to know the login credentials used by the test
to understand the test itself.

After the set up phase follows the execution phase. In this phase the first
created device object is used to send a :term:`shell command` to the configured
:term:`target device`. In this case a ``echo "hello"`` is sent and the response
is stored in a variable. Under the hood the :py:class:`~monk_tf.dev.Device`
object creates one or more connections to the :term:`target device`, transmits
the message in the corresponding protocol and collects the response. This is
the central feautre of :term:`MONK`. Just by calling one method the whole
complexity of the interaction gets handled by the framework and the user, in
this case the :term:`test case`, does not need to be concerned about the
details and can focus on which commands he wants to send to the
:term:`target device` and what the results should be. As you can see in the API
docs of the :py:class:`~monk_tf.dev.Device` class there are also other infos
that can be used after the communication happened, like the last prompt or the
return code of the command executed.

The next step in the example is the assert step. In this step all changes that
happened in the execute step are verified to be as expected. In this case we
only check that the ``echo`` really printed a *hello*.

The last step is the tear down step. In this step everything that was set up
for this test case is disconnected, removed or set back in its original state.
Usually high level languages often do not bother about this step, because the
garbage collector will take care of deleting all the objects that are not
needed anymore. However when using :term:`MONK` communication channels to the
:term:`target device` are connected and it might be wise to disconnect them on
purpose when the test is finished. In future versions of :term:`MONK` it might
also be possible that additional tear down steps might be included in the
configuration like shutting down the :term:`target device` or deleting test
artifacts. Therefore it is suggested to always include this line.

.. todo:: Explain the config file

Installation
------------

To install MONK you need ``pip``, a tool for installing and managing Python
packages, which you can get via your system's package manager, e.g.::

    $ sudo apt-get install python-pip

Afterwards (or if it was present to begin with), you can use it to install
MONK::

    $ pip install monk_tf

This step might require ``sudo`` rights. You might also consider setting up
MONK in a ``virtualenv``. You can check that the installation worked the
following way::

    $ python
    Python 2.7.3 (default, Aug  1 2012, 05:14:39) 
    [GCC 4.6.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import monk_tf
    >>> monk_tf.device.Device
    <class 'monk_tf.device.Device'>

If you also want to run unit tests for MONK you might want to read the
:doc:`developer instructions <contributing>`.

*****
Usage
*****

At this point of MONK's development usage mostly relies on your ability to
interact with the :doc:`API <modules>` and the
:doc:`development process <contributing>`.

When writing software tests, it is strongly recommended to structure them in
two parts:

 #. **the Test Framework**: which contains the code necessary to execute your tests.

 #. **the Test Cases**: the actual test code.


This structure stays the same, when using MONK. MONK is not a replacement for
the :term:`test framework`, it's merely an addition that simplifies both
parts.

When writing tests with MONK, you will usually want to use the
:py:class:`monk_tf.devicetestcase.DeviceTestcase` instead of the
:py:class:`unittest.TestCase`. An empty testcase might look like this:

.. literalinclude:: template_testcase.py
    :linenos:

Using the :py:class:`~monk_tf.devicetestcase.DeviceTestcase` automatically
enables some of the features currently implemented in MONK. For example, your
:term:`target device <target vs development system>` will be rebooted and
updated. Have a look at the source code of :py:mod:`~monk_tf.devicetestcase`
if you are interested in more details.

*********************
Patching MONK Locally 
*********************

As all users of MONK will have to be experienced software developers for the
foreseeable future, there might arise a lot of situations, where you might
want to apply local changes to MONK that the developers of MONK might not want
to add to the official repository or which will simply not be added fast
enough. Since Python itself works directly on its source code, you have many
options to patch your code locally. However, keep in mind that there is one
recommended way to do this and although you are, of course, free to use other
options as well, you will not get any support for them.

1. Import and Extend (Recommended)
==================================

The best way to change existing modules is extending their classes and using
your individual classes instead. As an example, let us assume you want to make
the ``conn`` attribute in :py:class:`~monk_tf.device.Device` optional, in
order to be able to add an individual connection later on, if needed. To do
this, you should add another class (say ``DeviceOptionalConn``) to the
directory of your test framework, which inherits from
:py:class:`monk_tf.device.Device`::

    import monk_tf as monk

    class DeviceOptionalConn(monk.device.Device):
        pass

You may then go ahead to apply your changes as desired::

    import monk_tf as monk

    class DeviceOptionalConn(monk.device.Device):

        def __init__(self, devtype):
            try:
                self._setp = Device.Device_Types[devtype.lower()]
            except KeyError:
                raise Exception("Unknown device type {}.".format(devtype))

            self.bcc = bcc.Bcc()
            rst = self.bcc.reset if self._setup['reset_cb'] == True else None
            atexit.register(self.__shutdown)
            
            if self._setup["network_setup"] is not None:
                self.conn = connection.Connection(
                    network_setup = self._setup['network_setup'],
                    login = self._setup['login'],
                    serial_skip_pw = self._setup['serial_skip_pw'],
                    reset_cb = rst
                )
            self._logger = logging.getLogger(__name__)

Instead of using :py:mod:`monk_tf.device.Device` you may then use
:py:mod:`testframework.DeviceOptionalConn` in your tests.


2. Patch the Install Folder
============================

Another way would be to navigate to the directory containing MONK and
directly overwrite the code. As MONK is an open source distribution,
this should be straightforward. It is, however, impossible to foresee
what will happen to your changes once you use ``pip``,e.g. to
update MONK. This method is thus not recommended.


3. Follow the MONK Developer Process
====================================

This is what you need to do if you want to have your changes applied
to the MONK project globally. See :doc:`contributing` for further
details about this point.
