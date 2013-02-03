#!/usr/bin/env python
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

import sys, os, inspect
sys.path.append(os.path.abspath(
    os.path.dirname(inspect.getfile(inspect.currentframe()))+"/../src/monk_tf"))

import unittest

from test_bcc import TestBcc
from test_connection import TestConnection
from test_device import TestDevice
from test_devicetestcase import TestDevicetestcase
from test_serial_conn import TestSerialConn
from test_ssh_conn import TestSshConn


class TestAll(unittest.TestSuite):
    
    def __init__(self):
        self.addTest(TestBcc())
        self.addTest(TestConnection())
        self.addTest(TestDevice())
        self.addTest(TestDeviceTestcase())
        self.addTest(TestSerialConn())
        self.addTest(TestSshConn())



if __name__ == "__main__":
    unittest.main()
