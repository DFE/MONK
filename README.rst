Intro
=====

Using MONk you can write tests like you would write unit tests, just that they
are able to interact with your embedded system.

Let's look at an example. In the following example we have an embedded system
with a serial terminal and a network interface. We want to write a test, which
checks whether the network interface receives correct information via dhcp.

The test case written with nosetests::

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
`API Docs <http://dfe.github.io/MONK/monk_tf.html>`_.
