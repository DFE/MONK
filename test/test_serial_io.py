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

import logging

from nose import tools as nt

from monk_tf import serial_io as sio


def test_simple():
    """serial_io: check wether creating a SerialIO object works
    """
    #nothing to prepare
    #
    #execute
    sut = sio.SerialIO()
    #assert
    nt.ok_(sut, "should contain a monk_tf.serial_io.SerialIO object, but instead contains this: '{}'".format(sut))


def test_cmd_set_attribs():
    """serial_io: check wether cmd automatically updates the attributes
    """
    # prepare
    send_cmd = "qwer"
    expected_calls = ['write', 'read_until']
    expected_cmd = send_cmd + "\n"
    expected_confidence = True
    expected_output = 'abcd'
    sut = MockSerialIOCmd((True, expected_output))
    # execute
    sut.cmd(send_cmd)
    # evaluate
    nt.eq_(expected_calls, sut.calls)
    nt.eq_(expected_cmd, sut.last_cmd)
    nt.eq_(expected_confidence, sut.last_confidence)
    nt.eq_(expected_output, sut.last_output)
    # clean up
    # not needed


def test_read_until_strips_end():
    """serial_io: check wether reading really strips end_strip
    """
    # prepare
    expected_calls = ["read"]
    expected_out = "trewq\n"
    expected_confidence = True
    in_strip = "abcd"
    in_sleep = 0.0
    in_mock_output = expected_out + in_strip
    sut = MockSerialIORead(in_mock_output)
    # execute
    out_confidence, output = sut.read_until(in_strip, sleep_time=in_sleep)
    # evalute
    nt.eq_(expected_calls, sut.calls)
    nt.eq_(expected_confidence, out_confidence)
    nt.eq_(expected_out, output)
    # clean up
    # not needed


def test_read_until_strips_start():
    """serial_io: check wether reading really strips start_strip
    """
    # prepare
    expected_calls = ["read", "read"]
    expected_out = "trewq\n"
    expected_confidence = True
    in_start_strip = "abcd\n"
    in_stop_strip = "dcba"
    in_sleep = 0.0
    in_mock_output = in_start_strip + expected_out + in_stop_strip
    sut = MockSerialIORead(in_mock_output)
    # execute
    out_confidence, output = sut.read_until(
            in_stop_strip,
            start_strip=in_start_strip,
            sleep_time=in_sleep
    )
    # evalute
    nt.eq_(expected_calls, sut.calls)
    nt.eq_(expected_confidence, out_confidence)
    nt.eq_(expected_out, output)
    # clean up
    # not needed


class MockSerialIOCmd(sio. SerialIO):
    """ mocks specifically for testing the cmd() method
    """

    def __init__(self, readout=None):
        self.calls = []
        self.readout = readout
        super(MockSerialIOCmd, self).__init__()


    def write(self,cmd=None):
        self.calls.append("write")


    def read_until(self, cmd=None, prompt=None, sleep_time=None, timeout=None,
            start_strip=None):
        self.calls.append("read_until")
        return self.readout


class MockSerialIORead(sio.SerialIO):

    def __init__(self, readout=None):
        self.calls = []
        self.readout = readout
        super(MockSerialIORead, self).__init__()


    def write(self,cmd=None):
        self.calls.append("write")


    def read(self, number=None):
        self.calls.append("read")
        return self.readout

    def inWaiting(self):
        return 0
