# -*- coding: utf-8 -*-
#
# MONK automated test framework
#
# Copyright (C) 2013 DResearch Fahrzeugelektronik GmbH
# Written and maintained by MONK Developers <project-monk@dresearch-fe.de>
#
# This program is free software; you can redistribute it and/or # modify it under the terms of the GNU General Public License
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
    sut.credentials = ("not", "important")
    # execute
    sut.connect()
    sut.login()
    after_login = sut.current_state
    out = sut.cmd(txt_in)
    sut.disconnect()
    # here no exceptions is already a good sign that fsm works
    # assert
    nt.eq_(sut.current_state, conn.Disconnected(),
            "after complete transition end state should be disconnected")
    nt.eq_(after_login, conn.Authenticated(),
            "after login, state should be authenticated")
    nt.eq_(out, expected, "cmd should return same message as was put in")

@nt.raises(conn.NotConnectedException)
def test_wrong_state():
    """ conn: raise Exception when sending cmd unconnected
    """
    # prepare
    sut = conn.EchoConnection()
    # execute
    sut.cmd("")
    # finished, because cmd should raise exception

def test_cmd_returncode():
    """ conn: test connections can handle additional parameters
    """
    # set up
    sut = conn.EchoConnection()
    sut2 = conn.DefectiveConnection()
    # execute + assert (raises Error if params can't be parsed)
    sut._cmd("hello", returncode=True)
    try:
        out = sut2._cmd("hello", returncode=True)
    except conn.MockConnectionException as e:
        pass

def test_connected_login():
    """ conn: connection's _login is not called if already logged in
    """
    # set up
    sut = MockConnection(start_state=conn.Authenticated())
    # execute
    sut.login()
    sut.login()
    sut.login()
    # assert
    nt.ok_("_login" not in sut.calls)

@nt.raises(conn.CantConnectException)
def test_legal_port():
    """ conn: using a non existing port results in exception
    """
    # setup
    sut = conn.SerialConnection(port="this/port/can/hopefully/not/exis.t")
    # exercise
    sut.connect()

@nt.raises(conn.CantConnectException)
def test_noprompt_exception():
    """ conn: connecting to shut down target device results in exception
    """
    # setup
    sut = conn.SilentConnection()
    # exercise
    sut.connect()

def test_noprompt_notconnected():
    """ conn: connecting to shut down target device doesn't change state
    """
    # setup
    sut = conn.SilentConnection()
    # exercise
    try:
        sut.connect()
    except conn.CantConnectException as e:
        # verify
        nt.ok_(isinstance(sut.current_state, conn.Disconnected))

class MockConnection(conn.AConnection):

    def __init__(self, *args, **kwargs):
        self.calls = []
        self.logged_in = kwargs.pop("logged_in", False)
        super(MockConnection, self).__init__(*args, **kwargs)

    def _connect(self):
        self.calls.add("_connect")

    def _login(self):
        self.calls.append("_login")
        self.logged_in = True

    def _cmd(self, *args, **kwargs):
        self.calls.add("_cmd")

    def _disconnect(self):
        self.calls.add("_disconnect")

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
