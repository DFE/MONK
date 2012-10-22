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

# This file will run all of G.O.R.D.O.N.s unit tests (i.e. the 
# tests testing the framework) using a test runner which checks
# for coverage as well as for actual test results.

# REQUIREMENTS
# ------------
# In order to run the tests you will need (ubuntu package):
# * the unittest2 module (python-unittest2)
# * coverage.py (python-coverage)
# * the coverage test runner (python-coverage-test-runner)

def run():
    from CoverageTestRunner import CoverageTestRunner
    import sys, os, inspect

    runner = CoverageTestRunner()
    for item in ("bcc", "connection", "device", "devicetestcase", "logger", "serial_conn", "ssh_conn"):
        runner.add_pair( item + ".py", "tests/test_" + item + ".py")
    runner.run()

if __name__ == "__main__":
    run()


