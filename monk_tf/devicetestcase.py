#!/usr/bin/env python
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
"""
Package for MONK integration test case generic test classes
"""

import unittest
import datetime
import device
import threading
import logging
import os

def config_logging():
    """ Configure the root logger """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    filename = "run-%s.log" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    handler = logging.FileHandler(filename, mode='w+')
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(filename)s::%(funcName)s(): "
        + "%(message)s"))
        
    logger.addHandler(handler)


class DeviceTestCase(unittest.TestCase):
    """ This class is the base class for all MONK tests. It takes
        care of basic device initialization and guarantees that there's only
        one instance of :py:class:`Device` active at any time. 
        
        Classes inheriting from :py:class:`DeviceTestCase` will automatically
        win a logger object and a device object upon initialization. These two
        instance objects are provided by :py:class:`DeviceTestCase` :

        .. code-block:: python
                
                import devicetestcase

                class MyTest(devicetestcase.DeviceTestCase):

                      ....

                    def setUp(self):
                        self.dev.wait_for_network()
                        self.logger.debug("Device IP is: %s." % self.dev.host)

                      ....
    """

    __dev = None
    __devsem = threading.Lock()
    
    
    @classmethod
    def get_device(cls, devicetype, nand_boot=True, init_logging=True):
        """ Get the :py:class:`Device` singleton instance. A new instance will
            be created if none is available yet. 
        """
        if not cls.__dev:
            cls.__devsem.acquire()
            if not cls.__dev:
                cls.__create_device(devicetype, nand_boot, init_logging=init_logging)
            cls.__devsem.release()
        return cls.__dev


    @classmethod        
    def __create_device(cls, devicetype, nand_boot=True, init_logging=True):
        """ boot HidaV-device to NAND """
        if init_logging:
            config_logging()
        cls.__dev = device.Device( devtype = devicetype )
        # checking the environment variable before reboot
        need_reboot = os.getenv("MONK_NEED_START_REBOOT", 1)
        if nand_boot and need_reboot == 0:
            logging.getLogger(__name__).debug("Boot to NAND ...")
            cls.__dev.reboot(to_nand=True)


    def __init__(self, devicetype, *args, **kwargs): # pragma: no cover
        """ The class will create and add to self logger and dev objects upon
            instantiation.
        """
        init_logging = True
        if 'init_logging' in kwargs:
            init_logging = kwargs["init_logging"]
            del kwargs["init_logging"]
        super(DeviceTestCase, self).__init__(*args, **kwargs)
        self.dev = DeviceTestCase.get_device(devicetype, init_logging=init_logging)
        self.logger = logging.getLogger(__name__)
        
