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

To install MONK you need ``pip``, which you can get via your system's
package manager, e.g.::

    $ sudo apt-get install python-pip

If you have it already installed, then you can do the following step::

    $ pip install monk_tf

This step might require ``sudo`` rights or should likely be executed in a
``virtualenv``. You can check that the installation worked in the following
way::

    $ python
    Python 2.7.3 (default, Aug  1 2012, 05:14:39) 
    [GCC 4.6.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import monk_tf
    >>> monk_tf.device.Device
    <class 'monk_tf.device.Device'>

If you also want to run the unittests for MONK you might want to follow the
:doc:`developer instructions <contributing>`.

*****
Usage
*****

At this point the usage mostly relies on your ability to interact with the
:doc:`API <api-docs>` and the :doc:`development process <contributing>`.

In general when writing tests it is expected, that you structure your software
tests in these two packages:

 #. **the Testframework**: which contains all the code for your tests.

 #. **The Testcases**: the actual test code.


This structure stays the same, when you use MONK. MONK is not a replacement for
the :term:`testframework`, it's merely an addition that simplifies both
packages.

In general when writing tests with MONK, you want to use the
:py:class:`monk_tf.devicetestcase.DeviceTestcase` instead of the
:py:class:`unittest.TestCase`. An empty testcase might look like that:

.. literalinclude:: template_testcase.py
    :linenos:

Using the :py:class:`~monk_tf.devicetestcase.DeviceTestcase` enables already
some of the features currently implemented in MONK. This will for example
reboot and update your :term:`target device`. Some things are already prepared
for you. Have a look at the source code of :py:mod:`~monk_tf.devicetestcase`.

*********************
Locally Patching MONK
*********************

Because all users of MONK have to be experienced software developers for the
foreseeable future, there might arise a lot of situations, where you
want to apply local changes to MONK that the developers of MONK might not want
to add to the official repository or which will simply not be added fast
enough. Since Python itself works directly on it's source code, you have many
options to patch your code locally. But keep in mind that there is one
recommended way to do things and although you are free to use other options as
well, you won't get any support for them.

1. Import and extend (recommended)
==================================

The best way to change existing modules is extending their classes and using
your individual classes instead. As an example let's say you want to make the
``conn`` attribute in :py:class:`~monk_tf.device.Device` optional, that you can
add an individual connection later on, if you want to. To do that, you will
first go to the folder of your own test framework and add another class
``DeviceOptionalConn``, which inherits
from :py:class:`monk_tf.device.Device`::

    import monk_tf as monk

    class DeviceOptionalConn(monk.device.Device):
        pass

Then you go ahead to apply your changes as desired::

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

Then instead of using :py:mod:`monk_tf.device.Device` you will use
:py:mod:`testframework.DeviceOptionalConn` in your tests.


2. Patch The Install Folder
============================

Another way would be to find the folder at which MONK is installed and
overwrite the code directly. Because MONK is always delivered as source
distribution, there should be no problem with that. It is unclear though what
happens with your changes once you patch the standard MONK.

3. Follow the MONK developer process
====================================

See :doc:`contributing` for further details about this point.
