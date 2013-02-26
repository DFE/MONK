..  MONK Testframework
    created on Mon Feb 11 2013
    (C) 2013, DResearch Fahrzeugelektronik GmbH

..  You can redistribute this file and/or modify it under the terms of the GNU
    General Public License as published by the Free Software Foundation; 
    either version 2 of the License, or (at your option) any later version

###############
Getting Started
###############

.. toctree::
    :maxdepth: 2

************
Installation
************

..  "a tool for installing and managing Python packages" is quoted from
    https://pypi.python.org/pypi/pip
    
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
interact with the :doc:`API <api-docs>` and the
:doc:`development process <contributing>`.

When writing software tests, it is strongly recommended to structure them in
two parts:

 #. **the Test Framework**: which contains the code necessary to execute
 your tests.

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
:term:`target device` will be rebooted and updated. Have a look at the source
code of :py:mod:`~monk_tf.devicetestcase` if you are interested in more
details.

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
what will happen to your changes once you use ``pip`` to, for example,
update MONK. This method is thus not recommended.


3. Follow the MONK Developer Process
====================================

This is what you need to do if you want to have your changes applied
to the MONK project globally. See :doc:`contributing` for further
details about this point.
