# -*- coding: utf-8 -*-
#
# MONK automated test framework
#
# Copyright (C) 2013 DResearch Fahrzeugelektronik GmbH
# Written and maintained by MONK Developers <project-monk@dresearch-fe.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 3 of the License, or (at your option) any later version.
#

from nose import tools as nt
from monk_tf import dev
from monk_tf import conn

def test_simple():
    """ dev: create Device
    """
    # execute
    sut = dev.Device()
    # assert
    nt.ok_(sut, "should have an object of dev.Device")

def test_send_cmd():
    """ dev: send cmd to EchoConnection
    """
    # prepare
    test_input = "just some text"
    expected_out = test_input
    sut = dev.Device(EchoConn())
    # execute
    out = sut.cmd(test_input)
    # assert
    nt.eq_(expected_out, out)

@nt.raises(dev.CantHandleException)
def test_no_conn():
    """ dev: let all connections fail
    """
    # prepare
    test_input = "no connection will succeed here"
    expected_out = test_input
    sut = dev.Device(DefectiveConn(), DefectiveConn())
    # execute
    out = sut.cmd(test_input)
    # catch exception

class EchoConn(object):
    def cmd(*args, **kwargs):
        return kwargs.pop("msg", "NOTHING")

class DefectiveConn(object):
    def cmd(*args, **kwargs):
        raise Exception("can't handle that")
