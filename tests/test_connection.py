#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#
# HidaV automated test framework connection class unit tests
#
# Copyright (C) 2012 DResearch Fahrzeugelektronik GmbH
# Written and maintained by Thilo Fromm <fromm@dresearch-fe.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 2 of the License, or (at your option) any later version.
#


import subprocess, atexit
import unittest

from copy import deepcopy

import sys, os, inspect
sys.path.append(os.path.abspath(
    os.path.dirname(inspect.getfile(inspect.currentframe()))+"/.."))

from connection import Connection
import serial_conn
import ssh_conn

#
# MOCKING
#

#  --- mocked functions ---

class MockSerialConn(object):
    instance = None
    __called = { "__init__" : [], 
                   "open"   : [],
                    "cmd"   : []  }
    called = {}

    def __init__(self, login, skip_pass, boot_prompt, reset_cb):
        MockSerialConn.called["__init__"].append(
            (login, skip_pass, boot_prompt, reset_cb) )
        MockSerialConn.instance = self

    def open(self):
        MockSerialConn.called["open"].append(True)

    def cmd(self, cmd):
        MockSerialConn.called["cmd"].append(cmd)
        if MOCK_sercmd_raise:
            raise MOCK_sercmd_raise
        return 0, MOCK_sercmd_ret


class MockSshConn(object):

    instance = None

    __called = { "__init__" : [], 
                 "cmd"      : []  }
    called = {}

    def __init__(self, host, login):
        MockSshConn.called["__init__"].append((host, login))
        MockSshConn.instance = self

    def cmd(self, cmd):
        MockSshConn.called["cmd"].append(cmd)
        if MOCK_sshcmd_raise:
            raise MOCK_sshcmd_raise
        return 0, MOCK_sshcmd_ret

# --- mock helper variables and functions ---

MOCK_sercmd_ret   = ""
MOCK_sercmd_raise = None
MOCK_sshcmd_ret   = ""
MOCK_sshcmd_raise = None

def mock_reset_values():
    global MOCK_sercmd_raise, MOCK_sercmd_ret, MOCK_sshcmd_raise, MOCK_sshcmd_ret
    MOCK_sercmd_raise = None
    MOCK_sercmd_ret   = ""
    MOCK_sshcmd_raise = None
    MOCK_sshcmd_ret   = ""
    MockSshConn.called      = deepcopy(MockSshConn._MockSshConn__called)
    MockSshConn.instance    = None
    MockSerialConn.called   = deepcopy(MockSerialConn._MockSerialConn__called)
    MockSerialConn.instance = None

orig_serial_conn = serial_conn.SerialConn
orig_ssh_conn    = ssh_conn.SshConn

def mock_on():
    mock_reset_values()
    serial_conn.SerialConn  = MockSerialConn
    ssh_conn.SshConn        = MockSshConn

def mock_off():
    serial_conn.SerialConn  = orig_serial_conn
    ssh_conn.SshConn        = orig_ssh_conn

# --- mocking ENDs ---
    
#
# The actual tests
#

class TestConnection(unittest.TestCase):
    """ This class implements a number of default test cases
        for the connection class."""

    def setUp(self):
        mock_on()

    def tearDown(self):
        mock_off()


    def test_default_init(self):
        """ Test the default initialization. 
            This will implicitly test _serial_setup() as well. """
        c = Connection(network_setup = ("hurz", "bla-if0"))

        # check instance vars
        self.assertEquals(c._login, ("root", ""))
        self.assertEquals(c._target_if, "bla-if0")
        self.assertEquals(c._serial, MockSerialConn.instance)
        self.assertEquals(c.host, "hurz")

        # check initialisation of serial_conn class
        self.assertEquals(len(MockSerialConn.called["__init__"]), 1)
        self.assertEquals(MockSerialConn.called["__init__"][0], 
                            (c._login, True, "HidaV boot on", None))
        self.assertEquals(len(MockSerialConn.called["open"]), 1)
        self.assertEquals(MockSerialConn.called["open"][0], True)


    def __ssh_test(self, c):
        s = c._ssh
        self.assertEquals(len(MockSshConn.called["__init__"]), 1)
        self.assertEquals(MockSshConn.called["__init__"][0], (c.host, c._login))

    def test_ssh(self):
        """ Test for the ssh property. """
        c = Connection(network_setup = ("horst", "if-fi0"))
        self.__ssh_test(c)

        # check for no initialization the second time 'round
        MockSshConn.called["__init__"] = []
        s = c._ssh
        self.assertEquals(len(MockSshConn.called["__init__"]), 0)

        # check for re-init after the property has been deleted
        del c._ssh
        self.__ssh_test(c)


    def test_host(self):
        """ Unittest for the host property. """
        c = Connection()

        # first, let the connection figure out the hot IP by itself
        global MOCK_sercmd_ret
        MOCK_sercmd_ret = "534.117.9.15"
        self.assertEquals(c.host, MOCK_sercmd_ret)

        # then, check whether we can set it
        c.host = "www.heise.de"
        self.assertEquals(c.host, "www.heise.de")

        # finally: check the deleter and the getter's exception handling
        del c.host
        MOCK_sercmd_ret = "unparseable IP address"
        self.assertRaises(Exception, lambda: c.host)
        del c.host


    def test_cmd(self):
        """ Test for the command dispatcher. """
        global MOCK_sercmd_ret, MOCK_sshcmd_ret, MOCK_sshcmd_raise
        MOCK_sercmd_ret = "Serial command execution"
        MOCK_sshcmd_ret = "SSH command execution"

        c = Connection(network_setup = ("hurz", "bla-if0"))
        MockSerialConn.called = deepcopy(MockSerialConn._MockSerialConn__called)

        # check for ssh command execution
        self.assertEquals(c.cmd("test-command"), (0, MOCK_sshcmd_ret))

        self.assertEquals(len(MockSshConn.called["cmd"]), 1)
        self.assertEquals(MockSshConn.called["cmd"][0], "test-command")
        self.assertEquals(len(MockSerialConn.called["cmd"]), 0)

        # generate an exception for ssh to check for serial execution
        MOCK_sshcmd_raise = Exception()
        self.assertEquals(c.cmd("test-2-command"), (0, MOCK_sercmd_ret))
        self.assertEquals(MockSerialConn.called["cmd"][0], "test-2-command")
        self.assertEquals(len(MockSerialConn.called["cmd"]), 1)


    def test_has_networking(self):
        """ Test for the networking availability checker. """
        global MOCK_sercmd_ret

        c = Connection()
        self.assertFalse(c.has_networking())

        MOCK_sercmd_ret = "123.456.789.012"
        self.assertTrue(c.has_networking())


if __name__ == "__main__":
    unittest.main()

