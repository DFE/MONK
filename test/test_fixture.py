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

from os.path import dirname, abspath
import inspect
import logging

from nose import tools as nt

from monk_tf import dev
from monk_tf import conn
from monk_tf import fixture

logger = logging.getLogger(__name__)
here = dirname(abspath(inspect.getfile(inspect.currentframe())))


def test_simple_xiniparser():
    """ fixture: use Xiniparser directly to create simple device
    """
    # set up
    sut = fixture.Fixture(lookfordbgsrc=False)
    props = fixture.XiniParser(here + "/example_fixture.cfg")
    expected_dev = dev.Device(conn.EchoConnection(name="echo1"))
    expected_dev.name = "dev1"
    # execute
    sut._update_props(props)
    sut._initialize()
    # assert
    # check if names and arguments are the same
    logger.debug("sut: " + str(sut))
    nt.eq_(expected_dev.name, sut.devs[0].name)
    expected_conn = expected_dev.conns[0]
    sut_conn = sut.devs[0].conns[0]
    nt.eq_(expected_conn.name, sut_conn.name)
    nt.eq_(expected_conn._args, sut_conn._args)
    nt.eq_(expected_conn._kwargs, sut_conn._kwargs)

def test_simple_fixture():
    """ fixture: use Fixture directly to create simple device
    """
    # set up
    expected_dev = dev.Device(conn.EchoConnection(name="echo1"))
    expected_dev.name = "dev1"
    # execute
    sut = fixture.Fixture(here + "/example_fixture.cfg",lookfordbgsrc=False)
    # assert
    # check again like previous test case
    logger.debug("sut: " + str(sut))
    nt.eq_(expected_dev.name, sut.devs[0].name)
    expected_conn = expected_dev.conns[0]
    sut_conn = sut.devs[0].conns[0]
    nt.eq_(expected_conn.name, sut_conn.name)
    nt.eq_(expected_conn._args, sut_conn._args)
    nt.eq_(expected_conn._kwargs, sut_conn._kwargs)

def test_update_fixture():
    """ fixture: update a Fixture with a second file
    """
    # set up
    expected_dev = dev.Device(conn.EchoConnection(name="echo3"))
    expected_dev.name = "dev1"
    sut = fixture.Fixture(here + "/example_fixture.cfg",lookfordbgsrc=False)
    # execute
    sut.read(here + "/example_fixture_update.cfg")
    # assert
    # check again like previous test case
    logger.debug("sut: " + str(sut))
    nt.eq_(expected_dev.name, sut.devs[0].name)
    expected_conn = expected_dev.conns[0]
    sut_conn = sut.devs[0].conns[0]
    nt.eq_(expected_conn.name, sut_conn.name)
    nt.eq_(expected_conn._args, sut_conn._args)
    nt.eq_(expected_conn._kwargs, sut_conn._kwargs)

def test_add_second_dev_update():
    """ fixture: update a second dev into Fixture
    """
    # set up
    expected_dev1 = dev.Device(conn.EchoConnection(name="echo1"))
    expected_dev2 = dev.Device(conn.EchoConnection(name="echo2"))
    expected_dev1.name = "dev1"
    expected_dev2.name = "dev2"
    sut = fixture.Fixture(here + "/example_fixture.cfg",lookfordbgsrc=False)
    logger.debug("sut-props-before:" + str(sut.props))
    # execute
    sut.read(here + "/example_fixture_dev2.cfg")
    # assert
    logger.debug("sut: " + str(sut))
    sut_dev1 = sut.devs[0] if sut.devs[0].name == "dev1" else sut.devs[1]
    sut_dev2 = sut.devs[1] if sut.devs[1].name == "dev2" else sut.devs[0]
    # check dev1
    nt.eq_(expected_dev1.name, sut_dev1.name)
    expected_conn = expected_dev1.conns[0]
    sut_conn = sut_dev1.conns[0]
    nt.eq_(expected_conn.name, sut_conn.name)
    nt.eq_(expected_conn._args, sut_conn._args)
    nt.eq_(expected_conn._kwargs, sut_conn._kwargs)
    # check dev2
    nt.eq_(expected_dev2.name, sut_dev2.name)
    expected_conn = expected_dev2.conns[0]
    sut_conn = sut_dev2.conns[0]
    nt.eq_(expected_conn.name, sut_conn.name)
    nt.eq_(expected_conn._args, sut_conn._args)
    nt.eq_(expected_conn._kwargs, sut_conn._kwargs)

@nt.raises(fixture.CantParseException)
def test_cant_parse_exception():
    """ fixture: reading a file without appropriate parser raises exception
    """
    # set up
    false_cfg_file = abspath(inspect.getfile(inspect.currentframe()))
    # execute
    sut = fixture.Fixture(false_cfg_file,lookfordbgsrc=False)

def test_fast_cmd():
    """ fixture: call first device's cmd
    """
    # setup
    sut = fixture.Fixture(lookfordbgsrc=False)
    sut.devs.append(dev.Device(conn.EchoConnection()))
    msg = "test"
    expected_out = msg
    # exercise
    out = sut.cmd(msg)
    # verify
    nt.eq_(expected_out, out)

@nt.raises(IOError)
def test_no_fixture_file():
    """ fixture: calling non existing fixture file raises IOError
    """
    # set up not necessary
    # exercise
    fixture.Fixture("this_file_does_not_exist.cfg",lookfordbgsrc=False)
