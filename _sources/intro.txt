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
    import monk_tf.fixture as mf

    def test_hi():
        """ send an echo and receive a hello
        """
        # set up
        h = mf.Fixture("target_device_login.cfg")
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
:py:class:`~monk_tf.fixture.Fixture` object is created and given the name of a
file. This file contains the information necessary to communicate with the
:term:`target device`, e.g., the information to access a serial connection and
login credentials. An example content will be
:ref:`discussed later<intro-cfg>`. The :py:class:`~monk_tf.fixture.Fixture`
object will read this file and create :term:`MONK` objects for you based on the
configuration. This helps to separate the information necessary to communicate
with a :term:`device<target device>` from the information that is important for
a :term:`test case`. As you see in the example it is not necessary to know the
login credentials used by the test to understand the test itself.

After the set up phase follows the execution phase. In this phase the first
created device object is used to send a :term:`shell command` to the configured
:term:`target device`. In this case a ``echo "hello"`` is sent and the response
is stored in a variable. Under the hood the :py:class:`~monk_tf.dev.Device`
object creates one or more connections to the :term:`target device`, transmits
the message in the corresponding protocol and collects the response. This is
the central feature of :term:`MONK`. Just by calling one method the whole
complexity of the interaction gets handled by the framework and the user, in
this case the :term:`test case`, does not need to be concerned about the
details and can focus on which commands he wants to send to the
:term:`target device` and what the results should be. As you can see in the API
docs of the :py:class:`~monk_tf.dev.Device` class there are also other infos
that can be used after the communication happened, like the last prompt or the
return code of the command executed.

The next step in the example is the assert step. In this step all changes that
happened in the execute step are verified to be as expected. In this case we
only check that the ``echo`` really printed a ``hello``.

The last step is the tear down step. In this step everything that was set up
for this test case is disconnected, removed or set back in its original state.
Usually high level languages do not bother about this step, because the garbage
collector will take care of deleting all the objects that are not needed
anymore. However when using :term:`MONK` communication channels to the
:term:`target device` are connected and it might be wise to disconnect them on
purpose when the test is finished. In future versions of :term:`MONK` it might
also be possible that additional tear down steps might be included in the
:term:`fixture files<fixture file>` like shutting down the
:term:`target device` or deleting test artifacts. Therefore it is suggested to
always include this line.

.. _intro-cfg:

Fixture Files
-------------

Fixture files are :term:`extended INI` (short Xini) files that contain the
information to create :term:`MONK` objects. In the code object in
:ref:`intro-solution` you see how they can be used together with a
:py:class:`~monk_tf.fixture.Fixture` object to create everything necessary to
run your tests with your :term:`target device`. To run this example the
following :term:`fixture file` could be used::

    [dev1]
        type = Device
        [[serial1]]
            type = SerialConnection
            user = test
            password = secret
            port = /dev/ttyUSB1
            baudrate = 115200
            timeout = 1.5

First it should be said that the indentation is optional. It is basically only
used for a better overview, meaning everything that belongs to an object is
indented related to its owner, e.g., ``type = Device`` is indented to
``[dev1]``, therefore it is an attribute of the object ``[dev1]``. If you blend
out the indentation you see a format not too different from the normal
:term:`INI` format you can often see in Python projects. The only difference to
normal :term:`INI` files is that ``serial1`` is surrounded by two pairs of
squared braces (``[[]]``). This means that ``serial1`` is not on the same
hierarchical level as ``dev1``, but is actually an attribute of ``dev1``.  You
can also see that from the indentation.

The example describes two objects, ``dev1`` and ``serial1``. ``dev1`` is the
main object of this file. The first attribute shows that it is of type
:py:class:`~monk_tf.dev.Device`. The second attribute is ``serial1``, which is
of type :py:class:`~monk_tf.conn.SerialConnection`. All other attributes belong
to ``serial1`` and describe what the :py:class:`~monk_tf.conn.SerialConnection`
should be initialized with.

This is the minimal definition you can use in a :term:`fixture file`: a
:py:class:`~monk_tf.dev.Device` and any implementation of an
:py:class:`~monk_tf.conn.AConnection`. Describing objects in
:term:`fixture files<fixture file>` allows you to reuse a definition, allows
non-programmers to change some configuration data like the username that is
used for tests, and it also decreases the information a person needs to
understand when reading a :term:`test case`. Therefore it is adviced to use
:term:`fixture files<fixture file>` as much as possible.

Sometimes it is not possible, though. In that case :term:`MONK` is built in 3
layers that allow you different tradeoffs between abstraction and control. More
about that in the next section.

.. _intro-layers:

The Layers
----------

:term:`MONK` is built in 3 layers, thereby allowing different tradeoffs between
abstraction and control. This is good for you, the user, because you can choose
the tradeoff that works best for your current task. It is also a helpful idea
in developing :term:`MONK`, because always when a layer of higher abstraction
is created or manipulated it makes use of a layer with a smaller degree of
abstraction and a higher degree of control. Let's look at some details.

The layer structure follows the logical structure of interaction with a
:term:`target device`:

 * The direct interaction to a :term:`target device` happens via direct access
   of connections like serial connections.

 * In a more complex scenario the :term:`target device` is understood as a
   whole and it is not so important what the different connections might be.
   Therefore :py:class:`~monk_tf.dev.Device` objects contain
   :py:class:`~monk_tf.conn.AConnection` objects. Instead of using the
   connections directly, the user mainly interacts with a
   :py:class:`~monk_tf.dev.Device` object.

 * When there are many :term:`test cases<test case>` that contain similar
   :py:class:`~monk_tf.dev.Device` objects then it makes sense to describe the
   :py:class:`~monk_tf.dev.Device` objects separately in config-like files, the
   :term:`fixture files<fixture file>`. Therefore the
   :py:class:`~monk_tf.fixture.Fixture` objects read external
   :term:`fixture files<fixture file>` and contain references to
   :py:class:`~monk_tf.dev.Device` objects. The user does not create
   :py:class:`~monk_tf.dev.Device` objects himself.

In layers it looks like this:

 * :py:mod:`monk_tf.conn` - The connection layer has the highest level of
   control in exchange for basically no abstraction. Every Exception needs to
   be handled by the user and every step of the connection workflow must be
   followed manually. In exchange everything that is done with the connections
   can be seen and influenced directly and no exceptions are ignored by the
   framework.

 * :py:mod:`monk_tf.dev` - The device layer handles connections directly.
   Connections can be added, removed and changed in order. How each connection
   is handled to transfer commands to the :term:`target device` is handled by
   the devices, though. Therefore this layer allows a balanced tradeoff between
   abstraction and control.

 * :py:mod:`monk_tf.fixture` - The fixture layer is the highest level of
   abstraction, with nearly no need to name details explicitely. The user can
   focus on writing the test without worrying how the data is transfered
   between :term:`test host` and :term:`target device`.

It is also possible to combine the layers in one :term:`test case`, e.g., a
:py:class:`~monk_tf.fixture.Fixture` object contains a reference to its devices
via its attribute :py:attr:`~monk_tf.fixtures.Fixture.devs`. This attribute
is basically a list of :py:class:`~monk_tf.dev.Device` objects. The same way
each :py:class:`~monk_tf.dev.Device` object contains a reference to its
connections via its attribute :py:attr:`~monk_tf.dev.Device.conns`. All objects
can be interacted with as if the corresponding layer was used in the first
place.

Installation
------------

To install :term:`MONK` you need ``pip``, a tool for installing and managing
Python packages, which you can get via your system's package manager, e.g., for
Debian based distributions::

    $ sudo apt-get install python-pip

Afterwards (or if it was present to begin with), you can use it to install
:term:`MONK`::

    $ pip install monk_tf

This step might require ``sudo`` rights. You might also consider setting up
MONK in a ``virtualenv``. You can check that the installation worked the
following way::

    $ python
    Python 2.7.3 (default, Aug  1 2012, 05:14:39) 
    [GCC 4.6.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import monk_tf.dev as md
    >>> md.Device
    <class 'monk_tf.dev.Device'>

If you also want to run unit tests for MONK you might want to read the
:doc:`developer instructions <contributing>`.

Side Note: Working with Different MONK Versions
-----------------------------------------------

When using :term:`MONK` a time will come in which updating to a newer version
of :term:`MONK` will require a lot of changes in your
:term:`test cases<test case>`. This leads to a situation in which you think you
have to choose between using a newer version of :term:`MONK` for its features
or using an older version of :term:`MONK` to keep the maintenance costs low. We
also faced this problem ad :term:`DFE`, therefore we developed a small helper
script that allows you to do both. If you already work well with
:term:`virtualenvs<virtualenv>` then you will have not much of a trouble.

The basic idea is that for each set of requirements (contain a specific
:term:`MONK` version) you create a separate suite. Thus if you have tests for
``monk_tf==0.1.1`` you keep all these tests in one suite. If you are starting
to write new tests now, you will probably write them for ``monk_tf==0.1.4``.
Therefore your new tests go into a new suite. If you decide now that you need
to do some work on an older :term:`test case` that worked with
``monk_tf==0.1.1``, you can also choose to leave it in the old suite or do the
required changes and move it to your new suite. If one day a ``monK_tf==0.1.5``
is released, you create a new suite, that contains all tests that work with
this version.

If you want to make use of a little helper, then have a look at 
`multisuite <https://pypi.python.org/pypi/multisuite/>`_.
