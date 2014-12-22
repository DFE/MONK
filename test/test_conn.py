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
    sut = conn.ConnectionBase('')
    # assert
    nt.ok_(sut, "should contain an AConnection object, but contains '{}'"
            .format(sut))

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
