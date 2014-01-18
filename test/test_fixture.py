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
from monk_tf import harness

logger = logging.getLogger(__name__)
here = dirname(abspath(inspect.getfile(inspect.currentframe())))

def test_simple_xiniparser():
    """ harness: use Xiniparser directly to create simple device
    """
    # set up
    sut = harness.Harness()
    props = harness.XiniParser(here + "/example_harness.cfg")
    expected_dev = dev.Device(conn.SerialConnection(
        name="serial1",
        port="/dev/ttyUSB0",
        user="testuser",
        password="secret1",
    ))
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

def test_simple_harness():
    """ harness: use Harness directly to create simple device
    """
    # set up
    expected_dev = dev.Device(conn.SerialConnection(
        name="serial1",
        port="/dev/ttyUSB0",
        user="testuser",
        password="secret1",
    ))
    expected_dev.name = "dev1"
    # execute
    sut = harness.Harness(here + "/example_harness.cfg")
    # assert
    # check again like previous test case
    logger.debug("sut: " + str(sut))
    nt.eq_(expected_dev.name, sut.devs[0].name)
    expected_conn = expected_dev.conns[0]
    sut_conn = sut.devs[0].conns[0]
    nt.eq_(expected_conn.name, sut_conn.name)
    nt.eq_(expected_conn._args, sut_conn._args)
    nt.eq_(expected_conn._kwargs, sut_conn._kwargs)

def test_update_harness():
    """ harness: update a Harness with a second file
    """
    # set up
    expected_dev = dev.Device(conn.SerialConnection(
        name="serial2",
        port="/dev/ttyUSB1",
        user="testuser2",
        password="secret2",
    ))
    expected_dev.name = "dev1"
    sut = harness.Harness(here + "/example_harness.cfg")
    # execute
    sut.read(here + "/example_harness_update.cfg")
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
    """ harness: update a second dev into Harness
    """
    # set up
    expected_dev1 = dev.Device(conn.SerialConnection(
        name="serial1",
        port="/dev/ttyUSB0",
        user="testuser",
        password="secret1",
    ))
    expected_dev2 = dev.Device(conn.SerialConnection(
        name="serial2",
        port="/dev/ttyUSB1",
        user="testuser2",
        password="secret2",
    ))
    expected_dev1.name = "dev1"
    expected_dev2.name = "dev2"
    sut = harness.Harness(here + "/example_harness.cfg")
    logger.debug("sut-props-before:" + str(sut.props))
    # execute
    sut.read(here + "/example_harness_dev2.cfg")
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

@nt.raises(harness.CantParseException)
def test_cant_parse_exception():
    """ harness: reading a file without appropriate parser raises exception
    """
    # set up
    false_cfg_file = abspath(inspect.getfile(inspect.currentframe()))
    # execute
    sut = harness.Harness(false_cfg_file)
