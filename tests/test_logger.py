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

from Gordon import logger


class LoggerTestCase(unittest2.TestCase):
    """ This class implements a number of default test cases
        for the logger tool class."""

    def test_singleton(self):
        """ Test the singleton property of our logger. """
        l1 = logger.init()
        l2 = logger.init()
        l3 = logger.init()
        l4 = logger.init()
        self.assertEquals(l1, l2)
        self.assertEquals(l1, l3)
        self.assertEquals(l1, l4)
        
