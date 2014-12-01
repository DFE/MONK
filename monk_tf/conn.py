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

import io
import os
import sys
import re
import logging
import time

import pexpect
from pexpect import pxssh
from pexpect import fdpexpect
import pyte

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

class CantCreateConn(ConnectionException):
    """ is raised when even several attempt were not able to create a connection.
    """
    pass

class NoRetcodeException(ConnectionException):
    """ is raised when the output doesn't contain a retcode for unknown reasons.
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



    def __init__(self, default_timeout=None, first_prompt_timeout=None):
        if hasattr(self, "name") and self.name:
            self._logger = logging.getLogger(self.name)
        else:
            self._logger = logging.getLogger(type(self).__name__)
        self.default_timeout = default_timeout or 30
        self.first_prompt_timeout = int(first_prompt_timeout) if first_prompt_timeout else 120
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
            self._sendline("stty -echo")
            self._expect(self.prompt)
            return self._exp

    def _expect(self, pattern, timeout=-1, searchwindowsize=-1):
        """ a wrapper for :pexpect:meth:`spawn.expect`
        """
        self.log("expect({},{},{})".format(
            str(pattern).encode('string-escape'),
            timeout,
            searchwindowsize,
        ))
        try:
            self.exp.expect(pattern, timeout, searchwindowsize)
            self.log("expect succeeded.")
        except Exception as e:
            self.log("expect failed with '{}'".format(
                e.__class__.__name__,
            ))
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

    def expect_prompt(self, timeout=None):
        self.log("expect prompt")
        self._sendline("")
        self._expect(self.prompt, timeout=timeout or self.default_timeout)

    def wait_for_prompt(self, timeout=-1):
        """
        """
        self.log("wait_for_prompt({})".format(
            timeout,
        ))
        end_time = time.time() + timeout
        while time.time() <= end_time:
            self.log("try prompt")
            try:
                self.expect_prompt(timeout)
                self._logger.debug("ready")
                break
            except (pexpect.EOF, pexpect.TIMEOUT) as e:
                self.log("could not retreive prompt")
                self.close()
                self.log("sleep before retry")
                time.sleep(3)

    def cmd(self, msg, timeout=-1, expect=None, do_retcode=True):
        """ send a shell command and retreive its output.
        """
        self._logger.debug("START cmd({},{},{},{})".format(
            msg,
            expect,
            timeout or self.default_timeout,
            do_retcode,
        ))
        self.wait_for_prompt(self.first_prompt_timeout)
        prepped_msg = self._prep_cmdmessage(msg, do_retcode)
        self._sendline(prepped_msg)
        try:
            self._expect(expect or self.prompt, timeout=timeout or self.default_timeout)
            self._logger.debug("SUCCESS: cmd({}) result='{}' expect-match='{}'".format(
                str(msg)[:15].encode("string_escape") + ("[...]" if len(str(msg)) > 15 else ""),
                str(self.exp.before)[:50].encode("string-escape") + ("[...]" if len(str(self.exp.before)) > 50 else ""),
                str(self.exp.after)[:50].encode("string-escape") + ("[...]" if len(str(self.exp.after)) > 50 else ""),
            ))
        except (pexpect.EOF, pexpect.TIMEOUT) as e:
            self.log("caught EOF/TIMEOUT on last expect; closing connections")
            self.close()
            raise e
        return self._prep_cmdoutput(self.exp.before, prepped_msg, do_retcode)

    def _prep_cmdmessage(self, msg, do_retcode=True):
        """ prepares a command message before it is delivered to pexpect

        It might add retreiving a returncode and strips unnecessary whitespace.
        """
        self.log("prep_msg({},{})".format(
            str(msg).encode("string-escape"),
            do_retcode,
        ))
        # If the connection is a shell, you might want a returncode.
        # If it is not (like drbcc) then you might have no way to retreive a
        # returncode. Therefore make a decision here.
        get_retcode = '; echo "<retcode>$?</retcode>"' if do_retcode else ""
        # strip each line for unnecessary whitespace and delete empty lines
        prepped = "\n".join(line.strip() for line in msg.split("\n") if line.strip())
        out = prepped+get_retcode
        self.log("prepped:'{}'".format(
            out.encode("string-escape"),
        ))
        return out

    def _prep_cmdoutput(self, out, cmd_expect, do_retcode=True):
        """ prepare the pexpect output for returning to the user

        Removing all the unnecessary "\r" characters and separates the
        returncode if one is requested.
        """
        self.log("prep_out({},{})".format(
            str(out).encode("string-escape"),
            do_retcode,
        ))
        if not out:
            self.log("out was empty and therefore couldn't be prepped.")
            return None, out
        # replace everything else
        stream = pyte.Stream()
        capture = Capture()
        stream.attach(capture, only=["draw", "linefeed"])
        stream.feed(out)
        prepped_out = str(capture)
        if do_retcode:
            try:
                match = re.search("\n?<retcode>(\d+)</retcode>.*\n", prepped_out)
                self.log("found retcode string '{}'".format(
                    str(match.group(0)).encode("string-escape"),
                ))
                retcode = int(match.group(1))
                prepped_out = prepped_out.replace(match.group(0), "")
                self.log("prepped with retcode")
                return retcode, prepped_out
            except (AttributeError, IndexError) as e:
                self._logger.exception(e)
                raise NoRetcodeException("failed to find retcode with '{}'. Formatted output:'{}'".format(
                            e.__class__.__name__,
                            prepped_out.encode("string-escape"),
                ))
        else:
            self.log("prepped without retcode")
            return None, prepped_out

    def close(self):
        self.log("close connection")
        try:
            self._exp.close()
            del self._exp
            self.log("successfully closed connection")
        except AttributeError:
            self.log("connection already closed")
            pass

    def __del__(self):
        self.log("getting deleted")
        self.close()
        self.log("bye.")


class SerialConn(ConnectionBase):
    """ implements a serial connection.
    """

    def __init__(self, name, port, user, pw,
            prompt="\r?\n?[^\n]*#",
            default_timeout=None,
            first_prompt_timeout=None,
        ):
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
        super(SerialConn, self).__init__(
                default_timeout=default_timeout,
                first_prompt_timeout=first_prompt_timeout,
        )

    def _get_exp(self):
        spawn = fdpexpect.fdspawn(os.open(self.port, os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY))
        self._sendline()
        self._expect("(?i)login: ")
        self._sendline(user or self.user)
        self._expect("(?i)password: ")
        self._sendline(pw or self.pw)
        self._expect(self.prompt)
        return spawn

    def _login(self, user=None, pw=None):
        self._logger.debug("serial._login({},{})".format(user, pw))

class SshConn(ConnectionBase):
    """ implements an ssh connection.
    """

    def __init__(self, name, host, user, pw,
            prompt=None,
            default_timeout=None,
            force_password=True,
            first_prompt_timeout=None,
            login_timeout=10,
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
        self.force_password = force_password
        self.login_timeout = int(login_timeout)
        if prompt:
            self._logger.warning("ssh connection ignores attribute prompt, because it sets its own prompt")
        super(SshConn, self).__init__(
                default_timeout=default_timeout,
                first_prompt_timeout=first_prompt_timeout,
        )

    @property
    def prompt(self):
        self.log("retreive ssh PROMPT")
        return self.exp.PROMPT

    def _get_exp(self):
        self.log("create pxssh object")
        end_time = time.time() + self.first_prompt_timeout
        while time.time() < end_time:
            self.log("try creating pxssh object")
            try:
                s = pxssh.pxssh(echo=False)
                s.force_password = self.force_password
                s.login(
                        server=self.host,
                        username=self.user,
                        password=self.pw,
                        login_timeout=self.login_timeout,
                )
                return s
            except (pxssh.ExceptionPxssh, pexpect.EOF, pexpect.TIMEOUT) as e:
                self.log("wait a little before retry creating pxssh object")
                time.sleep(3)
        raise CantCreateConn("tried for '{}' seconds".format(self.first_prompt_timeout))

    def expect_prompt(self, timeout=None):
        self.log("ssh expect prompt")
        self._sendline("")
        self.exp.prompt(timeout or self.default_timeout or -1)

    def close(self):
        self.log("force pxssh object to logout")
        try:
            self._exp.logout()
        except Exception as e:
            self.log("while logging out caught the following exception, can often be ignored")
            self._logger.exception(e)
        super(SshConn, self).close()

class Capture(object):

    def __init__(self, handle=None):
        self.handle = handle or io.StringIO()

    def draw(self, ch, **flags):
        self.handle.write(unicode(ch))

    def linefeed(self):
        self.handle.write(u"\n")

    def __str__(self):
        self.handle.seek(0)
        return self.handle.read()
