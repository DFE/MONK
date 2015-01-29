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

import collections

from nose import tools as nt
from monk_tf import conn


def test_simplest():
    """ conn: create the simplest possible AConnection
    """
    # execute
    sut = conn.ConnectionBase('')
    # verify
    nt.ok_(sut)

def test_send_echo():
    """ conn: send echo 123 and receive 123
    """
    # setup
    sut = MockConn(name='', out="123")
    expected_retcode = 0
    expected_out = "123"
    # execute
    retcode, out = sut.cmd("echo 123", do_retcode=False)
    # verify
    nt.eq_(out, expected_out)

@nt.raises(AttributeError)
def test_close_successfully():
    """ conn: after closing there's no connection any more
    """
    # setup
    sut = MockConn(name='', out="123")
    # execute
    sut.close()
    # verify
    sut._exp

# does it recover?

class MockConn(conn.ConnectionBase):

    def __init__(self, *args, **kwargs):
        self._exp = Exp()
        self._exp.before = kwargs.pop("out", None)
        self._exp.after = ""
        super(MockConn, self).__init__(*args, **kwargs)
        self._calls = collections.defaultdict(list)
        self.prompt = self._exp.before

    def wait_for_prompt(*args, **kwargs):
        pass

    def _expect(self, pattern, timeout=-1, searchwindowsize=-1):
        self._calls["_expect"].append((pattern, timeout, searchwindowsize))

    def _send(self, pattern, timeout=-1, searchwindowsize=-1):
        self._calls["_send"].append((pattern, timeout, searchwindowsize))

    def _sendline(self, pattern, timeout=-1, searchwindowsize=-1):
        self._calls["_sendline"].append((pattern, timeout, searchwindowsize))

    @property
    def exp(self):
        return self._exp

class Exp(object):
    def close(self):
        pass
