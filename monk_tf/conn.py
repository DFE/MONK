# -*- coding: utf-8 -*-
#
# MONK automated test framework
#
# Copyright (C) 2013 DResearch Fahrzeugelektronik GmbH
# Written and maintained by MONK Developers <project-monk@dresearch-fe.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version # 3 of the License, or (at your option) any later version.  #

"""
This module implements connection handling. Using the classes from this module
you can connect directly to a :term:`target device` via serial or ssh.
Example::

    import monk_tf.conn as mc
    # create a serial connection
    serial=mc.SerialConn(port="/dev/ttyUSB3", user="tester", pw="test")
    # create a ssh connection
    ssh=mc.SshConn(host="192.168.2.123", user="tester", pw="test")
    # send a command
    print serial.cmd("ls -al")
    [...]
    # send a command
    ssh.cmd("ls -al")
    [...]
"""

import os
import sys
import re
import logging

import pexpect
from pexpect import fdpexpect

class ConnectionBase(object):
    """ is the base class for all connections.

    Don't instantiate this class directly.

    This class implements the behaviour of cmd() interactions, and it makes
    sure that it doesn't login a user that is already logged in.

    Extending this class requires to implement _get_exp() and _login().
    """



    def __init__(self):
        if hasattr(self, "name"):
            self._logger = logging.getLogger(self.name)
        else:
            self._logger = logging.getLogger(type(self).__name__)
        self._logger.debug("hi.")

    @property
    def exp(self):
        """ the pexpect object - Don't bother with this if you don't know what
                                 it means.
        """
        try:
            return self._exp
        except AttributeError as e:
            self._exp = self._get_exp()
            return self._exp

    def login(self, user=None, pw=None, timeout=30):
        """ attempts to authenticate to the connection.

        Default for user and password are the one's given to the connection on
        instantiation.

        :param user: the username
        :param pw: the password
        :param timeout: how long the connection waits to see whether it is
                        logged in already
        """
        self._logger.debug("login({},{},{})".format(user, pw, timeout))
        try:
            self.exp.sendline("")
            self.exp.expect(self.prompt, timeout=timeout)
            self._logger.debug("already logged in")
        except pexpect.TIMEOUT as e:
            self._login(user, pw)

    def cmd(self, msg, expect=None, timeout=30, login_timeout=None):
        """ send a shell command and retreive its output.

        :param msg: the shell command
        :param expect: a regex that represents the end of an interaction.
                       Defaults to the prompt set on connection instantiation
        :param timeout: how long a command call should wait for its desired
                        result
        :param login_timeout: how long the connection should wait until it
                              decides a login is necessary.

        :return: the stdout and stderr of the shell command
        """
        self._logger.debug("cmd({},{},{},{})".format(
            msg, expect, timeout, login_timeout))
        self.login(timeout=login_timeout or timeout)
        self.exp.sendline(msg)
        expect_msg = re.escape(msg[:5]) + "[^\n]*\r\n"
        self._logger.debug("expect:" + expect_msg.encode("string-escape"))
        self.exp.expect(expect_msg, timeout=timeout)
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
    """ implements a serial connection.
    """

    def __init__(self, name, port, user, pw, prompt="\r?\n?[^\n]*#"):
        """
        :param name: the name of the connection
        :param port: the path to the device file that is used for this connection
        :param user: the user name for the login
        :param pw: the password for the login
        :param prompt: the default prompt to check for
        """
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
    """ implements an ssh connection.
    """

    def __init__(self, name, host, user, pw, prompt="\r?\n?[^\n]*#"):
        """
        :param name: the name of the connection
        :param host: the URL to the device
        :param user: the user name for the login
        :param pw: the password for the login
        :param prompt: the default prompt to check for
        """
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
