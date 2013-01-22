#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#
# MONK Automated Testing Framework
#
# Copyright (C) 2012 DResearch Fahrzeugelektronik GmbH
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 2 of the License, or (at your option) any later version.
#


import unittest

import sys, os, inspect
sys.path.append(os.path.abspath(
    os.path.dirname(inspect.getfile(inspect.currentframe()))+"/../src/monk_tf"))

import device
from devicetestcase import DeviceTestCase

#
# MOCKING
#

#  --- mocked functions ---

class MockDevice(object):
    def __init__(self, devtype):
        pass
    def reboot(self, to_nand):
        pass

# --- mock helper variables and functions ---

orig_device      = device.Device


def mock_reset_values():
    pass

def mock_on():
    device.Device = MockDevice

def mock_off():
    device.Device = orig_device

# --- mocking ENDs ---
    
#
# The actual tests
#

class TestDevicetestcase(unittest.TestCase):
    """ This class implements a number of default test cases
        for the devicetestcase class."""
    def setUp(self):
        mock_on()

    def tearDown(self):
        mock_off()


    def test_get_device(self):
        dev = DeviceTestCase.get_device( "test-dev" )



if __name__ == '__main__':
    unittest.main()
