#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#
# HidaV automated test framework board controller class unit tests
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
import unittest2

import sys, os, inspect
sys.path.append(os.path.abspath(
    os.path.dirname(inspect.getfile(inspect.currentframe()))+"/.."))

from Gordon import Bcc, logger


# mocking area
MOCK_atexit_func = None
def mock_atexit_register(func):
        global MOCK_atexit_func 
        MOCK_atexit_func = func

class MockLogger(object):
    def debug(*args, **kwargs):
        pass
ML = MockLogger()

def mock_logger_init():
    return ML


MOCK_subp_retval = ""
MOCK_subp_input = [ ]

def mock_check_output(cmd, stderr = None):
    MOCK_subp_input.append([cmd, stderr])
    return MOCK_subp_retval

orig_log_init = logger.init
orig_ate_register = atexit.register
orig_subp_check_output = subprocess.check_output

def mock_on():
    logger.init             = mock_logger_init
    atexit.register         = mock_atexit_register
    subprocess.check_output = mock_check_output
    
def mock_off():
    logger.init             = orig_log_init
    atexit.register         = orig_ate_register
    subprocess.check_output = orig_subp_check_output
    global MOCK_subp_input 
    MOCK_subp_input = [ ]
    global MOCK_subp_retval
    MOCK_subp_retval = ""
    

# the actual tests

class BccTestCase(unittest2.TestCase):
    """ This class implements a number of default test cases
        for the board controller class."""

    def setUp(self):
        mock_on()
        pass

    def tearDown(self):
        mock_off()
        pass

    def test_default_init_cleanup(self):
        """ Test the default initialization and cleanup.
            This test just checks for the correct defaults after
            Bcc class instantiation. """

        b = Bcc()

        # check instance variables
        self.assertEquals(b._Bcc__drbcc,   "drbcc")
        self.assertEquals(b._Bcc__port,    "/dev/ttyUSB0")
        self.assertEquals(b._Bcc__port_br,  57600)
        self.assertEquals(b.logger,         ML)

        # check function registered with atexit
        self.assertEquals(b._Bcc__cleanup, MOCK_atexit_func)
        
        # check board controller commands issued during init
        global MOCK_subp_input
        self.assertEquals(len(MOCK_subp_input), 3)
        self.assertEquals(MOCK_subp_input[0], 
            [['drbcc', '--dev=/dev/ttyUSB0,57600', '--cmd=debugset 16,0100010001'], subprocess.STDOUT])
        self.assertEquals(MOCK_subp_input[1], 
            [['drbcc', '--dev=/dev/ttyUSB0,57600', '--cmd=heartbeat 65535'], subprocess.STDOUT])
        self.assertEquals(MOCK_subp_input[2],
            [['drbcc', '--dev=/dev/ttyUSB0,57600', '--cmd=hdpower 1'], subprocess.STDOUT])

        # check atexit command
        MOCK_subp_input = []
        MOCK_atexit_func()
        self.assertEquals(len(MOCK_subp_input), 1)
        self.assertEquals(MOCK_subp_input[0], 
            [['drbcc', '--dev=/dev/ttyUSB0,57600', '--cmd=debugset 16,00'], subprocess.STDOUT])

if __name__ == "__main__":
    unittest2.main()

