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

#
# MOCKING
#

#  --- mocked functions ---
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

def mock_check_output(cmd, stderr = None):
    MOCK_subp_input.append([cmd, stderr])
    if MOCK_subp_raise:
        raise MOCK_subp_raise
    return MOCK_subp_retval

# --- mock helper variables and functions ---

MOCK_bcc_example_output_off = """status_cb: raw data: 01 00 02 00 00 00 17 0b 09 00 09 00 e7 00 09 0a 04 ac 00 f0 00 60 02 05 01 4e 00 9e 00 4f 00 00 00 00 00 00 05 
SPIs/SPOs: Ignition: off, HDD-Sense: closed, OXE_INT1: 0, OXE_INT2: 0, XOSC_ERR: 0, GPI-Power: off, HDD-Power: off
GPInputs 1..6: 0 0 0 0 0 0   GPOutputs 1..4: 0 0 0 0  RTC Temp : 23 deg C  Accel X, Y, Z: 35mg, 35mg, 902mg
Voltages: 23.14V  11.96V  2.40V  0.96V  5.17V  3.34V  1.58V  0.79V  0.00V"""

MOCK_bcc_example_output_on = """status_cb: raw data: 01 00 02 00 00 00 17 0b 09 00 09 00 e7 00 09 0a 04 ac 00 f0 00 60 02 05 01 4e 00 9e 00 4f 00 00 00 00 00 00 05 
SPIs/SPOs: Ignition: on, HDD-Sense: closed, OXE_INT1: 0, OXE_INT2: 0, XOSC_ERR: 0, GPI-Power: off, HDD-Power: on
GPInputs 1..6: 0 0 0 0 0 0   GPOutputs 1..4: 0 0 0 0  RTC Temp : 23 deg C  Accel X, Y, Z: 35mg, 35mg, 902mg
Voltages: 23.14V  11.96V  2.40V  0.96V  5.17V  3.34V  1.58V  0.79V  0.00V"""

MOCK_bcc_example_output_debugget = """debug_get_cb: addr: 0x00000001 len: 4 data: 12 34 23 42"""

MOCK_subp_retval = ""
MOCK_subp_input = [ ]
MOCK_subp_raise = None

def mock_reset_values():
    global MOCK_subp_input, MOCK_subp_retval, MOCK_subp_raise
    MOCK_subp_input = [ ]
    MOCK_subp_retval = ""
    MOCK_subp_raise = None

orig_log_init = logger.init
orig_ate_register = atexit.register
orig_subp_check_output = subprocess.check_output

def mock_on():
    mock_reset_values()
    logger.init             = mock_logger_init
    atexit.register         = mock_atexit_register
    subprocess.check_output = mock_check_output
    
def mock_off():
    logger.init             = orig_log_init
    atexit.register         = orig_ate_register
    subprocess.check_output = orig_subp_check_output

# --- mocking ENDs ---
    
#
# The actual tests
#

class BccTestCase(unittest2.TestCase):
    """ This class implements a number of default test cases
        for the board controller class."""

    def setUp(self):
        mock_on()

    def tearDown(self):
        mock_off()


    def test_default_init_cleanup(self):
        """ Test the default initialization and cleanup.
            This test just checks for the correct defaults after
            Bcc class instantiation. 
            Note that this test also implicitly tests bcc.poweron(),
            which in turn tests bcc.hddpower and bcc.heartbeat setters."""

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


    def test_cleanup_fails(self):
        """ This test checks for pokemon exception handling 
            in the cleanup atexit handler. """
        b = Bcc()
        global MOCK_subp_raise
        MOCK_subp_raise = Exception()
        try:
            MOCK_atexit_func()
        except:
            self.fail("BCC atexit function raised an exception!")


    def __simple_setup(self, output, exc=None):
        """ Helper for setting up simple tests. Will create a bcc instance and
            do some initial cleanup. """
        b = Bcc()
        global MOCK_subp_input, MOCK_subp_retval, MOCK_subp_raise
        MOCK_subp_input = []
        MOCK_subp_retval = output
        if exc:
            MOCK_subp_raise = exc
        return b


    def test_cmd(self):
        """ Test the execution of an arbitrary command """

        b = self.__simple_setup("InDiesemStringDaSitztEinGeistUswUsf")

        rc, text = b.cmd("hurz")

        self.assertEquals(len(MOCK_subp_input), 1)
        self.assertEquals(MOCK_subp_input[0][0][2],'--cmd=hurz')

        self.assertEquals(text, MOCK_subp_retval)
        self.assertEquals(rc, 0)


    def test_cmd_fails(self):
        """ Test the execution of an arbitrary command which fails """

        b = self.__simple_setup("bla", subprocess.CalledProcessError(9, "", "exception output"))

        rc, text = b.cmd("narf")

        self.assertEquals(len(MOCK_subp_input), 1)
        self.assertEquals(MOCK_subp_input[0][0][2],'--cmd=narf')

        self.assertEquals(text, "exception output")
        self.assertEquals(rc, 9)


    def test_reset(self):
        """ Test the reset function. """

        import time
        b = Bcc()

        called = [ 0, 0, 0 ]
        s = time.sleep
        def cb(a, idx):
            a[idx] += 1

        try:
            b.poweroff = lambda: cb(called, 0)
            time.sleep = lambda ignored: cb(called, 1)
            b.poweron  = lambda: cb(called, 2)
            
            b.reset()

            self.assertEquals(called, [1,1,1])
        finally:
            time.sleep = s


    def test_poweroff(self):
        """ Poweroff test. Note that bcc.poweron() is already tested
            by test_default_init_cleanup(). """
        b = self.__simple_setup("");

        b.poweroff()

        self.assertEquals(len(MOCK_subp_input), 3)
        self.assertEquals(MOCK_subp_input[0], 
            [['drbcc', '--dev=/dev/ttyUSB0,57600', '--cmd=debugset 16,0100000001'], subprocess.STDOUT])
        self.assertEquals(MOCK_subp_input[1], 
            [['drbcc', '--dev=/dev/ttyUSB0,57600', '--cmd=heartbeat 0'], subprocess.STDOUT])
        self.assertEquals(MOCK_subp_input[2],
            [['drbcc', '--dev=/dev/ttyUSB0,57600', '--cmd=hdpower 0'], subprocess.STDOUT])

        
    def test_status(self):
        """ Test the bcc status property. """

        b = self.__simple_setup(MOCK_bcc_example_output_off)
        text = b.status

        self.assertEquals(len(MOCK_subp_input), 1)
        self.assertEquals(MOCK_subp_input[0][0][2],'--cmd=gets')

        self.assertEquals(text, MOCK_bcc_example_output_off)


    def test_ignition(self):
        """ Test the ignition prperty. """
        b = self.__simple_setup(MOCK_bcc_example_output_off)
        self.assertFalse(b.ignition)

        b = self.__simple_setup(MOCK_bcc_example_output_on)
        self.assertTrue(b.ignition)


    def test_hddpower(self):
        """ Test the hdd power prperty. """
        b = self.__simple_setup(MOCK_bcc_example_output_off)
        self.assertFalse(b.hddpower)

        b = self.__simple_setup(MOCK_bcc_example_output_on)
        self.assertTrue(b.hddpower)


    def test_heartbeat(self):
        """ test the heartbeat property. """
        b = self.__simple_setup(MOCK_bcc_example_output_debugget)

        curr, maxi = b.heartbeat

        self.assertEquals(curr, 4660)
        self.assertEquals(maxi, 9026)


if __name__ == "__main__":
    unittest2.main()

