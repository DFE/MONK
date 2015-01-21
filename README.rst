.. image:: https://travis-ci.org/DFE/MONK.svg
    :target: https://travis-ci.org/DFE/MONK
    :alt: Build Status

.. image:: https://readthedocs.org/projects/monk-tf/badge/?version=latest
    :target: https://readthedocs.org/projects/monk-tf/?badge=latest
    :alt: Documentation Status

.. image:: https://www.codacy.com/project/badge/f54aa09a5caa49549d9946f6f062b0de
    :target: https://www.codacy.com/public/erikbernoth/MONK
    :alt: Codacy Quality

.. image:: https://coveralls.io/repos/DFE/MONK/badge.svg
    :target: https://coveralls.io/r/DFE/MONK
    :alt: Coveralls Quality

.. image:: https://pypip.in/license/monk_tf/badge.svg
    :target: https://pypi.python.org/pypi/monk_tf
    :alt: License

.. image:: https://pypip.in/download/monk_tf/badge.svg
    :target: https://pypi.python.org/pypi/monk_tf
    :alt: Downloads

.. image:: https://pypip.in/version/monk_tf/badge.svg
    :target: https://pypi.python.org/pypi/monk_tf
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/monk_tf/badge.svg
    :target: https://pypi.python.org/pypi/monk_tf
    :alt: Supported Python Versions

.. image:: https://pypip.in/status/monk_tf/badge.svg
    :target: https://pypi.python.org/pypi/monk_tf
    :alt: Current Devel Status

.. image:: https://pypip.in/format/monk_tf/badge.svg
    :target: https://pypi.python.org/pypi/monk_tf
    :alt: Support Package Format


Intro
=====

Using MONK you can write tests like you would write unit tests, just that they
are able to interact with your embedded system.

Let's look at an example. In the following example we have an embedded system
with a serial terminal and a network interface. We want to write a test, which
checks whether the network interface receives correct information via dhcp.

The test case written with nosetests:

.. code-block:: python

    import nose.tools as nt

    import monk_tf.conn as mc
    import monk_tf.dev as md

    def test_dhcp():
        """ check whether dhcp is implemented correctly
        """
        # setup
        device = md.Device(mc.SerialConn('/dev/ttyUSB1','root','sosecure'))
        # exercise
        device.cmd('dhcpc -i eth0')
        # verify
        ifconfig_out = device.cmd('ifconfig eth0')
        nt.ok_('192.168.2.100' in ifconfig_out)

Even for non python programmers it should be not hard to guess, that this test
will connect to a serial interface on ``/dev/ttyUSB1``, send the shell command
``dhcpc`` to get a new IP adress for the ``eth0`` interface, and in the end it
checks whether the received IP address that the tester would expect. No need to
worry about connection handling, login and session handling.

For more information see the
`API Docs <http://monk-tf.readthedocs.org/en/latest/monk_tf.html>`_.
