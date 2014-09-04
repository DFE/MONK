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

############
#
# Exceptions
#
############

class ConnectionException(Exception):
    """ Base class for Exceptions from this module
    """
    pass

class BccException(ConnectionException):
    """ is raised to explain some BCC behaviour
    """
    pass

class NoBCCException(BccException):
    """ is raised when the BCC class does not find the drbcc tool needed for
        execution.
    """
    pass

#############
#
# Connections
#
#############

class ConnectionBase(object):
    """ is the base class for all connections.

    Don't instantiate this class directly.

    This class implements the behaviour of cmd() interactions, and it makes
    sure that it doesn't login a user that is already logged in.

    Extending this class requires to implement _get_exp() and _login().
    """



    def __init__(self):
        if hasattr(self, "name") and self.name:
            self._logger = logging.getLogger(self.name)
        else:
            self._logger = logging.getLogger(type(self).__name__)
        # make sure a pexpect object is created
        self.exp != False
        self.log("hi.")

    def log(self, msg):
        self._logger.debug(msg)

    @property
    def exp(self):
        """ the pexpect object - Don't bother with this if you don't know what
                                 it means.
        """
        self.log("retrieve pexpect object")
        try:
            return self._exp
        except AttributeError as e:
            self.log("have no pexpect object yet")
            self._exp = self._get_exp()
            return self._exp

    def _expect(self, pattern, timeout=-1, searchwindowsize=-1):
        """ a wrapper for :pexpect:meth:`spawn.expect`
        """
        self.log("expect({},{},{})".format(
            str(pattern).encode('string-escape'), timeout, searchwindowsize))
        try:
            self.exp.expect(pattern, timeout, searchwindowsize)
            self.log("expect succeeded.")
        except Exception as e:
            self.log("expect failed.")
            self._logger.exception(e)
            raise e

    def _send(self, s):
        """ a wrapper for :pexpect:meth:`spawn.send`
        """
        self._logger.debug("send({})".format(s))
        try:
            self.exp.send(s)
            self._logger.debug("send succeeded.")
        except Exception as e:
            self._logger.debug("send failed.")
            raise e

    def _sendline(self, s=""):
        """ a wrapper for :pexpect:meth:`spawn.sendline`
        """
        self._logger.debug("sendline({})".format(s))
        try:
            self.exp.sendline(s)
            self._logger.debug("sendline succeeded.")
        except Exception as e:
            self._logger.debug("sendline failed.(has pexpect? {})".format(
                        "yes" if self.exp else "no",
            ))
            raise e

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
            self._sendline("")
            self._expect(self.prompt, timeout=timeout)
            self._logger.debug("already logged in")
        except pexpect.TIMEOUT as e:
            self._login(user, pw)

    def cmd(self, msg, expect=None, timeout=30, login_timeout=None, do_retcode=True):
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
        prepped_msg = self._prep_cmdmessage(msg)
        self._sendline(prepped_msg)
        # expect the last 10 characters of the cmd message
        self._expect(re.escape(prepped_msg[-10:]) + "[^\n]*\r\n", timeout=timeout)
        self._expect(expect or self.prompt, timeout=timeout)
        self._logger.debug("cmd({}) result='{}' expect-match='{}'".format(
            str(msg[:15]).encode("string_escape") + ("[...]" if len(msg) > 15 else ""),
            str(self.exp.before[:50]).encode("string-escape") + ("[...]" if len(self.exp.before) > 50 else ""),
            str(self.exp.after[:50]).encode("string-escape") + ("[...]" if len(self.exp.after) > 50 else ""),
        ))
        return self._prep_cmdoutput(self.exp.before)

    def _prep_cmdmessage(self, msg, do_retcode=True):
        """ prepares a command message before it is delivered to pexpect

        It might add retreiving a returncode and strips unnecessary whitespace.
        """
        # If the connection is a shell, you might want a returncode.
        # If it is not (like drbcc) then you might have no way to retreive a
        # returncode. Therefore make a decision here.
        get_retcode = "; echo $?" if do_retcode else ""
        # strip each line for unnecessary whitespace and delete empty lines
        prepped = "\n".join(line.strip() for line in msg.split("\n") if line.strip())
        return prepped + get_retcode

    def _prep_cmdoutput(self, out, do_retcode=True):
        """ prepare the pexpect output for returning to the user

        Removing all the unnecessary "\r" characters and separates the
        returncode if one is requested.
        """
        prepped_out = out.replace("\r","")
        if do_retcode:
            splitted = prepped_out.split("\n")
            return int(splitted[-1]), "\n".join(splitted[:-1])
        else:
            return None, prepped_out


    def close(self):
        self.log("force pexpect object to close")
        self.exp.close(force=True)

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
        self._expect("[lL]ogin: ")
        self._sendline(user or self.user)
        self._expect("[pP]assword: ")
        self._sendline(pw or self.pw)
        self._expect(self.prompt)

class SshConn(ConnectionBase):
    """ implements an ssh connection.
    """

    def __init__(self, name, host, user, pw,
            prompt="\r?\n?[^\n]*#",
            tcpkeepalive=True,
            serveraliveinterval=10,
            serveralivecountmax=3,
            stricthostkeychecking=False,
        ):
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
        self.tcpkeepalive = tcpkeepalive
        self.serveraliveinterval = serveraliveinterval
        self.serveralivecountmax = serveralivecountmax
        self.stricthostkeychecking = stricthostkeychecking
        super(SshConn, self).__init__()

    def _get_exp(self):
        return pexpect.spawn("ssh {}@{} -o TCPKeepAlive={} -o ServerAliveInterval={} -o ServerAliveCountMax={} -o StrictHostKeyChecking={}".format(
            self.user,
            self.host,
            "yes" if self.tcpkeepalive else "no",
            self.serveraliveinterval,
            self.serveralivecountmax,
            "yes" if self.stricthostkeychecking else "no",
        ))
    def _login(self, user=None, pw=None):
        self._logger.debug("ssh._login({},{})".format(user, pw))
        self._expect("[pP]assword: ")
        self._sendline(pw or self.pw)
        self._expect(self.prompt)

###############################################################
#
# Others - Connections that don't have a normal shell interface
#
###############################################################

class BCC(ConnectionBase):

    def __init__(self, port, speed="57600", name=None, prompt="\r?\n?drbcc> "):
        if os.system("hash drbcc"):
            raise NoBCCException("Please install the DResearch drbcc tool!")
        self.name = name
        self.port = port
        self.speed = speed
        self.prompt = prompt
        super(BCC, self).__init__()

    def login(self,*args,**kwargs):
        try:
            super(BCC,self).login(*args,**kwargs)
        except pexpect.EOF as e:
            self._logger.exception(e)
            raise BccException("EOF found. Did you configure the correct port?")

    def _get_exp(self):
        self.log("_get_exp() with port '{}' and speed '{}'".format(
                        self.port,
                        self.speed,
        ))
        try:
            return pexpect.spawn("drbcc --dev={},{}".format(
                            self.port,
                            self.speed,
            ))
        except Exception as e:
            self.log("caught exception while spawning")
            self._logger.exception(e)
            raise e

    def _login(self, user=None, pw=None):
        self.log("_login() unnecessary for BCC")
        pass
