#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#
# GORDON Automated Testing Framework
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

class TestSerialConn(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
