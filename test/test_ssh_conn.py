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

from monk_tf import ssh_conn as msc

def test_simple():
    """check if creating a SshConn object works
    """
    # prepare
    test_host = None
    # execute
    sut = msc.SshConn(test_host)
    # assert
    nt.ok_(sut, "should contain a monk_tf.ssh_conn.SshConn object, but instead contains this: '{}'".format(sut))


def test_cmd_closes_without_exception():
    """check if closing without exception is called without waiting
    """
    # prepare
    sut = MockSshConn()
    expected = ['close()']
    # execute
    sut.cmd()
    # assert
    nt.eq_(expected, sut.calls, "expected '{}', but got '{}'".format(expected, sut.calls))


def test_cmd_closes_with_exception():
    """check if closing with exception is called without waiting
    """
    # prepare
    sut = MockSshConn(close_callback=raise_exception)
    expected = ['close()', 'wait_closed()']
    # execute
    sut.cmd()
    # assert
    nt.eq_(expected, sut.calls, "expected '{}', but got '{}'".format(expected, sut.calls))


# --------------- HELPERS -------------------------------

def raise_exception():
    """ a callback that raises a simple Exception
    """
    raise Exception()


class MockSshConn(msc.SshConn):


    def __init__(self, close_callback=None):
        mock_host = "ignore me"
        super(MockSshConn, self).__init__(mock_host)
        self.calls = []
        if close_callback is not None:
            self.close_callback = close_callback
        else:
            self.close_callback = self.empty_callback


    def cmd(self, txt=None):
        exec_txt = txt if txt is not None else "ignore the command text"
        return super(MockSshConn, self).cmd(exec_txt)


    def empty_callback(self):
        pass


    def _session(self):
        return self


    def open_session(self):
        return self


    def execute(self, throw_away):
        return 0


    def read(self, throw_away):
        return ""


    def close(self):
        self.calls.append('close()')
        self.close_callback()
        return 0


    def wait_closed(self):
        self.calls.append('wait_closed()')


    def exit_status(self):
        return 0
