# -*- coding: utf-8 -*-
#
# Copyright (C) 2012, 2013 DResearch Fahrzeugelektronik GmbH
# Maintained by project-monk@dresearch-fe.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging

from nose import tools as nt

from monk_tf import serial_conn as msc


def test_simple():
    """checks if creating a SerialConn object works
    """
    #nothing to prepare
    #
    #execute
    sut = msc.SerialConn()
    #assert
    nt.ok_(sut, "should contain a monk_tf.serial_conn.SerialConn object, but instead contains this: '{}'".format(sut))


def test_setting_read_timeout():
    """shall test if read timeouts are set properly

    The test mocks the pyserial API for setting this timeout. The API
    contains a class Serial with the parameter `timeout`
    (http://pyserial.sourceforge.net/pyserial_api.html#serial.Serial.timeout).
    This is originally defined in `pyserial/serial/util.py` in class
    `SerialBase` with the property-function `setTimeout`.

    This test comes wit the MockSerial class underneath the TestCase, which
    also contains this setter. But instead of setting real timeouts it
    simply stores all values in a list this test. Afterwards those values
    can be evaluated to find if the API seriously was used as expected.
    """
    #prepare
    start_rto = 591
    set_rto = -234
    #this contains always 2 calls, because read_until always writes both
    # read- and writeTimeout
    expected_rto = [
            set_rto,   #written into old_rto
            set_rto,   #written into old_wto
            start_rto, #written from old_rto
            None       #written from old_wto, which wasn't set
    ]
    target = "doesn't matter,rto" #just needed to fulfill API
    sut = MockSerial(rto=start_rto, target=target)
    #execute
    msc.SerialConn.read_until(sut, target, timeout=set_rto)
    #assert
    nt.eq_(expected_rto, sut.results,
            "expected: '{}', found: '{}'".format(expected_rto, sut.results))


def test_setting_write_timeout():
    """shall test if write timeouts are set properly

    The test mocks the pyserial API for setting this timeout. The API
    contains a class Serial with the parameter `writeTimeout`
    (http://pyserial.sourceforge.net/pyserial_api.html#serial.Serial.writeTimeout).
    This is originally defined in `pyserial/serial/util.py` in class
    `SerialBase` with the property-function `setTimeout`.

    This test comes wit the MockSerial class underneath the TestCase, which
    also contains this setter. But instead of setting real timeouts it
    simply stores all values in a list this test. Afterwards those values
    can be evaluated to find if the API seriously was used as expected.
    """
    #prepare
    start_wto = 195
    set_wto = -342
    #this contains always 2 calls, because read_until always writes both
    # read- and writeTimeout
    expected_wto = [
            set_wto,   #written into old_rto
            set_wto,   #written into old_wto
            None,      #written from old_rto, which wasn't set
            start_wto  #written from old_wto
    ]
    target = "doesn't matter,wto" #just needed to fulfill API
    sut = MockSerial(wto=start_wto, target=target)
    #execute
    msc.SerialConn.read_until(sut, target, timeout=set_wto)
    #assert
    nt.eq_(expected_wto, sut.results,
            "expected: '{}', found: '{}'".format(expected_wto, sut.results))


class MockSerial(msc.SerialConn):
    """mocks the :py:class:`serial.Serial` API

    It provides API like :py:class:`serial.Serial` and stores setter call
    results for comparison.
    """

    def __init__(self,rto=None, wto=None,target=None):
        self._rto = rto
        self._wto = wto
        self.target = target
        self.results = []
        self._logger = logging.getLogger(__name__)


    @property
    def timeout(self):
        return self._rto


    @timeout.setter
    def timeout(self,rto):
        self.results.append(rto)
        self._rto = rto


    @property
    def writeTimeout(self):
        return self._wto


    @writeTimeout.setter
    def writeTimeout(self,wto):
        self.results.append(wto)
        self._wto = wto

    def read(self):
        """ignore me.

        :py:func:`serial_conn.SerialConn.read_until()` expects to call this
        function, which is the only reason for it's existance.
        """
        return self.target
