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
from monk_tf import conn

def test_simplest():
    """ conn: create the simplest possible AConnection
    """
    # nothing to prepare
    # execute
    sut = conn.AConnection()
    # assert
    nt.ok_(sut, "should contain an AConnection object, but contains '{}'"
            .format(sut))

def test_call_methods():
    """ conn: calling a public AConnection method calls its state's method
    """
    # prepare
    state = MockState()
    expected_calls = ["connect", "login", "cmd", "disconnect"]
    sut = conn.AConnection(start_state=state)
    # execute
    sut.connect()
    sut.login()
    sut.cmd(None)
    sut.disconnect()
    # assert
    nt.eq_(expected_calls, state.calls,
            "didn't call the following methods: \"{}\"".format(
                list(set(expected_calls) - set(state.calls))))

def test_fsm():
    """ conn: go through all state transitions
    """
    # prepare
    txt_in = "qwerty12345"
    expected = txt_in
    sut = conn.EchoConnection()
    # execute
    sut.connect()
    sut.login()
    out = sut.cmd(txt_in)
    sut.disconnect()
    # here no exceptions is already a good sign that fsm works
    # assert
    nt.eq_(sut.current_state, conn.Disconnected(),
            "after complete transition end state should be disconnected")
    nt.eq_(out, expected, "cmd should return same message as was put in")


class MockState(conn.AState):
    calls = []

    def connect(self, connection):
        self.calls.append("connect")

    def login(self, connection):
        self.calls.append("login")

    def cmd(self, connection, msg):
        self.calls.append("cmd")

    def disconnect(self, connection):
        self.calls.append("disconnect")

    def next_state(self, connection):
        return self
