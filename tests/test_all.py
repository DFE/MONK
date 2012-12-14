#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#
# HidaV automated test framework unit test runner
#
# Copyright (C) 2012 DResearch Fahrzeugelektronik GmbH
# Written and maintained by Thilo Fromm <fromm@dresearch-fe.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 2 of the License, or (at your option) any later version.
#

import sys, os, inspect
sys.path.append(os.path.abspath(
        os.path.dirname(inspect.getfile(inspect.currentframe()))+"/.."))

import unittest

from test_bcc import TestBcc
from test_connection import TestConnection
from test_devicetestcase import TestDevicetestcase


class TestAll(unittest.TestSuite):
    
    def __init__(self):
        self.addTest(TestBcc())
        self.addTest(TestConnection())
        self.addTest(TestDeviceTestcase())



if __name__ == "__main__":
    unittest.main()
