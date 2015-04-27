# -*- coding: utf-8 -*-
#
# MONK automated test framework
#
# Copyright (C) 2015 DResearch Fahrzeugelektronik GmbH
# Written and maintained by MONK Developers <project-monk@dresearch-fe.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 3 of the License, or (at your option) any later version.
#

"""
This module contains the base classes and possibly other useful stuff
"""

import logging

class MonkException(Exception):
    """ base class for all monk_tf exceptions
    """
    pass

class MonkObject(object):
    """ base class for all Monkery

    mostly handles name setting and the object specific logging
    """

    def __init__(self, name=None, module=None):
        # must be set first, because it is used later on
        self.module = module
        self.name = name
        self.log("hi.")

    @property
    def name(self):
        try:
            return self._logger.name
        except:
            self.name = None
            return self._logger.name

    @name.setter
    def name(self, name):
        self._logger = logging.getLogger("{}.{}".format(
            self.module,
            name or self.__class__.__name__,
        ))

    def log(self, msg):
        """ sends a debug-level message to the logger

        This method is used so often, that a smaller version of it is quite
        comfortable.
        """
        self._logger.debug(msg)

    def testlog(self, msg):
        """ sends a warning-level message to the logger

        This method is used mostly in the test cases, that a smaller version
        of it is quite comfortable.
        """
        self._logger.warning(msg)
