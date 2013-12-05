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

""" Device Layer

This layer abstracts a complete :term:`target device` in a single object, which
can be interacted without worries about how the actual communication is done.

To use this module create a :py:class:`~monk_tf.dev.Device` class.

The package is separated into module exceptions and the device classes.
"""

import logging

import conn

logger = logging.getLogger(__name__)

############
#
# Exceptions
#
############

class DeviceException(Exception):
    """ base class for Exceptions of the device layer
    """
    pass

class CantHandleException(DeviceException):
    """ a request can't be handled by the connections of a :py:class:`~monk_tf.dev.Device`.
    """
    pass


##############################
#
# Devices - currently just one
#
##############################

class Device(object):
    """ a :term:`target device` abstraction
    """

    def __init__(self, *args, **kwargs):
        """
        :param conns: list of connections. The following works as well::

            Device(OneConnection(...), AnotherConnection(...),...)

        :param name: Device name for logging purposes.
        """
        self.conns = kwargs.pop("conns", list(args))
        self.name = kwargs.pop("name", self.__class__.__name__)

    def cmd(self, msg):
        """ send a :term:`shell command` to the :term:`target device`
        :param msg: the :term:`shell command`.
        :return: the standard output of the :term:`shell command`.
        """
        for connection in self.conns:
            try:
                connection.connect()
                connection.login()
                return connection.cmd(msg)
            except conn.ConnectionException as excpt:
                logger.exception("{}:{}:{}".format(
                    self.name,
                    connection.name,
                    excpt
                ))
        # no connection was able to get to the return statement
        raise CantHandleException("dev:'{}',conns:'{}':couldn't send cmd '{}'".format(
            self.name,
            map(str, self.conns),
            msg,
        ))

    def __del__(self):
        """ make sure all connections get closed on delete
        """
        for connection in self.conns:
            try:
                connection.close()
            except Exception as excpt:
                logger.exception(excpt)
