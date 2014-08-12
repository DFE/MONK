# -*- coding: utf-8 -*-
#
# MONK automated test framework
#
# Copyright (C) 2013 DResearch Fahrzeugelektronik GmbH
# Written and maintained by MONK Developers <project-monk@dresearch-fe.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 3 of the License, or (at your option) any later version.
#

"""

This module implements the lowest layer of interaction with a
:term:`target device`, the connection layer. This means that you can use this
module to create :py:class:`~monk_tf.conn.AConnection` objects, interact with
them, and manipulate their internal states.

States are implemented based on the State design pattern via
:py:class:`~monk_tf.conn.AState`. Connection objects hold a
:py:attr:`~monk_tf.conn.AConnection.current_state` attribute. Every time a
public method of a connection is called, the object will forward this call
to its :py:attr:`~monk_tf.conn.AConnection.current_state`, which will
then execute the method depending on what the task of the state is.

As an Example, let's take a :py:class:`~monk_tf.conn.SerialConnection`. If you
execute its :py:meth:`~monk_tf.conn.AConnection.connect` method, the connection
will delegate this task to its
:py:attr:`~monk_tf.conn.AConnection.current_state` which is probably a
:py:class:`~monk_tf.conn.Disconnected` object but might be any other state as
well. Each State object also has a method for each public
:py:class:`~monk_tf.conn.AConnection` method, e.g.,
:py:meth:`~monk_tf.conn.Disconnected.connect`, which makes it clear which
:py:class:`~monk_tf.conn.AState` method will be called from the
:py:class:`~monk_tf.conn.AConnection`. In this
:py:class:`~monk_tf.conn.AConnection` method there might be some checks (not in
this case, though) and then it will redirect the task to a private method of
:py:class:`~monk_tf.conn.SerialConnection`, in this case
:py:meth:`~monk_tf.conn.SerialConnection._connect`. Because this private method
expects that all checks are done it will attempt to initiate the connection.

This does not just seem complicated, it actually is. The reason is that the
State design pattern was applied here. To wrap your head around the idea might
be complicated at first but it also comes with great payoff. For example, when
you write a new child class of :py:class:`~monk_tf.conn.AConnection` you
overwrite the methods :py:meth:`~monk_tf.conn.AConnection._connect`,
:py:meth:`~monk_tf.conn.AConnection._login`,
:py:meth:`~monk_tf.conn.AConnection._cmd`, and
:py:meth:`~monk_tf.conn.AConnection._disconnect` to show how your connection
handles the different events. Because the State design pattern was chosen you
do not have to worry about checking if the connection is really ready for what
you want to do in this event, e.g., in
:py:meth:`~monk_tf.conn.AConnection._cmd` you do not need to worry if you are
already connected or not, because this has already been asserted by
:py:class:`~monk_tf.conn.AConnection` and the State design pattern. You can
expect to have a direct connection to the :term:`target device` and can start
writing the code that is necessary to send a :term:`shell command` to the
device.

Something else that might be confusing about this layer is that many methods
have undefined return behaviour. This is a disadvantage and a feature of Python
at the same time, because in Python there is no way to ensure that a method
only returns some specific type or result. Here we use it as a feature, because
from private methods like :py:meth:`~monk_tf.conn.AConnection._login` that
you implement in individual :py:class:`~monk_tf.conn.AConnection` child classes,
you can be sure that your return results get delivered to the publicly called
:py:meth:`~monk_tf.conn.AConnection.login`. And because Python does not force
us to define a specific return result you can choose in your private methods if
you want to return something and if so what it might be. In
:py:class:`~monk_tf.conn.SerialConnection` we decided to not return anything.
Therefore anybody who might decide to check what gets returned basically just
reads``None`` as the result and that is fine.

The code of this module is split into the following parts:
    1. *Exceptions* - all exceptions that are used in this module
    2. *AConnection* - the abstract connection class which all other
       connections are based on
    3. *Test Connections* - a list of connections that do not really connect to
       a :term:`target device` but instead are used for debugging purposes of
       your test cases
    4. *Real Connections* - the real connections that connect MONK to a
       :term:`target device`
    5. *AState* - the abstract State class which all other states are based on
    6. *State Classes* - the implementation of the state machine

-------------------------------------------------------------------------------

This module implements connection handling. Using the classes from this module
you can connect directly to a :term:`target device` via serial or ssh.
Example::

    # create a serial connection
    serial=SerialConn(port="/dev/ttyUSB3", user="tester", pw="test")
    # create a ssh connection
    ssh=SshConn(host="192.168.2.123", user="tester", pw="test")
    # send a command
    serial.cmd("ls -al")
    # send a command
    ssh.cmd("ls -al")
"""

import os
import sys
import re
import logging

import pexpect
from pexpect import fdpexpect

class ConnectionBase(object):
    """ is the base class for all connections.
    """



    def __init__(self):
        if hasattr(self, "name"):
            self._logger = logging.getLogger(self.name)
        else:
            self._logger = logging.getLogger(type(self).__name__)
        self._logger.debug("hi.")

    @property
    def exp(self):
        try:
            return self._exp
        except AttributeError as e:
            self._exp = self._get_exp()
            return self._exp

    def login(self, user=None, pw=None, timeout=30):
        self._logger.debug("login({},{},{})".format(user, pw, timeout))
        try:
            self.exp.sendline("")
            self.exp.expect(self.prompt, timeout=timeout)
            self._logger.debug("already logged in")
        except pexpect.TIMEOUT as e:
            self._login(user, pw)

    def cmd(self, msg, expect=None, timeout=30, login_timeout=None):
        self._logger.debug("cmd({},{},{},{})".format(
            msg, expect, timeout, login_timeout))
        self.login(timeout=login_timeout or timeout)
        self.exp.sendline(msg)
        expect_msg = re.escape(msg[:5]) + "[^\n]*\r\n"
        self._logger.debug("expect:" + expect_msg.encode("string-escape"))
        self.exp.expect(expect_msg, timeout=timeout)
        if False: #"rm" in msg:
            raise Exception("DIE MONK:" + str(self.exp))
        self._logger.debug("expect:" + (expect or self.prompt).encode("string-escape"))
        self.exp.expect(expect or self.prompt, timeout=timeout)
        self._logger.debug("cmd({}) result='{}' expect-match='{}'".format(
            str(msg[:15]).encode("string_escape") + ("[...]" if len(msg) > 15 else ""),
            str(self.exp.before[:50]).encode("string-escape") + ("[...]" if len(self.exp.before) > 50 else ""),
            str(self.exp.after[:50]).encode("string-escape") + ("[...]" if len(self.exp.after) > 50 else ""),
        ))
        return self.exp.before

    def __del__(self):
        self._logger.debug("bye.")
        self.exp.close()

class SerialConn(ConnectionBase):

    def __init__(self, name, port, user, pw, prompt="\r?\n?[^\n]*#"):
        self.name = name
        self.port = port
        self.user = user
        self.pw = pw
        self.prompt = prompt
        super(SerialConn, self).__init__()

    def _get_exp(self):
        spawn = fdpexpect.fdspawn(os.open(self.port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY))
        #spawn.logfile = sys.stdout
        return spawn

    def _login(self, user=None, pw=None):
        self._logger.debug("serial._login({},{})".format(user, pw))
        self.exp.expect("[lL]ogin: ")
        self.exp.sendline(user or self.user)
        self.exp.expect("[pP]assword: ")
        self.exp.sendline(pw or self.pw)
        self.exp.expect(self.prompt)

class SshConn(ConnectionBase):

    def __init__(self, name, host, user, pw, prompt="\r?\n?[^\n]*#"):
        self.name = name
        self.host= host
        self.user = user
        self.pw = pw
        self.prompt = prompt
        super(SshConn, self).__init__()

    def _get_exp(self):
        return pexpect.spawn("ssh {}@{} -o TCPKeepAlive=yes -o ServerAliveInterval=5 -o ServerAliveCountMax=3".format(
            self.user,
            self.host
        ))

    def _login(self, user=None, pw=None):
        self._logger.debug("ssh._login({},{})".format(user, pw))
        self.exp.expect("[pP]assword: ")
        self.exp.sendline(pw or self.pw)
        self.exp.expect(self.prompt)
