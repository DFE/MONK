# -*- coding: utf-8 -*-
#
# MONK Automated Testing Framework
#
# Copyright (C) 2012-2013 DResearch Fahrzeugelektronik GmbH, project-monk@dresearch-fe.de
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 3 of the License, or (at you option) any later version.
#

from nose import tools as nt

from monk_tf import serial_io as sio


def test_simple():
    """ serial_io: create a SerialIO Object without problems
    """
    # set up
    # exec
    sut = sio.SerialIO()
    # assert
    nt.ok_(isinstance(sut,sio.SerialIO),
        "should have type SerialIO, but has {}".format(type(sut)))


def test_cmd_hello_world():
    """ serial_io: cmd("hello") returns "world"
    """
    # set up
    any_txt = "hello"
    expected_out = "world"
    expected_calls = ["write('{}\n')".format(any_txt), "readall()"]
    sut = MockSerial()
    sut.out = "hello\n{}\n<prompt>$ ".format(expected_out)
    # exec
    out = sut.cmd(any_txt)
    # assert
    nt.eq_(expected_out, out)
    nt.eq_(expected_calls, sut.calls)


def test_cmd_with_windows_newlines():
    """ serial_io: make sure that windows newlines get replaced
    """
    # set up
    any_txt = "hello"
    expected_out = "world"
    expected_calls = ["write('{}\n')".format(any_txt), "readall()"]
    sut = MockSerial()
    sut._linesep = "\n"
    sut.out = "hello\n\r{}\n\r<prompt>$ ".format(expected_out)
    # exec
    out = sut.cmd(any_txt)
    # assert
    nt.eq_(expected_out, out)
    nt.eq_(expected_calls, sut.calls)


class MockSerial(sio.SerialIO):


    def __init__(self):
        self.calls = []


    def readall(self):
        self.calls.append("readall()")
        return self.out

    def write(self,msg):
        self.calls.append("write('{}')".format(msg))
