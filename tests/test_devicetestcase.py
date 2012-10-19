#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#
# HidaV automated test framework connectino class unit tests
#
# Copyright (C) 2012 DResearch Fahrzeugelektronik GmbH
# Written and maintained by Thilo Fromm <fromm@dresearch-fe.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 2 of the License, or (at your option) any later version.
#


import unittest2

import sys, os, inspect
sys.path.append(os.path.abspath(
    os.path.dirname(inspect.getfile(inspect.currentframe()))+"/.."))

from Gordon import logger, device, DeviceTestCase

#
# MOCKING
#

#  --- mocked functions ---

class MockLogger(object):
    def debug(*args, **kwargs):
        pass
    def info(*args, **kwargs):
        pass
    def exception(*args, **kwargs):
        pass
ML = MockLogger()

def mock_logger_init():
    return ML

class MockDevice(object):
    def __init__(self, devtype):
        pass
    def reboot(self, to_nand):
        pass

# --- mock helper variables and functions ---

orig_device      = device.Device
orig_log_init    = logger.init


def mock_reset_values():
    pass

def mock_on():
    logger.init   = mock_logger_init
    device.Device = MockDevice

def mock_off():
    logger.init   = orig_log_init
    device.Device = orig_device

# --- mocking ENDs ---
    
#
# The actual tests
#

class DeviceTestCaseTestCase(unittest2.TestCase):
    """ This class implements a number of default test cases
        for the connection class."""
    def setUp(self):
        mock_on()

    def tearDown(self):
        mock_off()


    def test_get_device(self):
        dev = DeviceTestCase.get_device( "test-dev" )



