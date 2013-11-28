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

import logging

import conn

logger = logging.getLogger(__name__)

class DeviceException(Exception):
    """ base class for Exceptions of the device layer
    """
    pass

class CantHandleException(DeviceException):
    """ is raised, when a request can't be handled by the connections of a
    :py:class:`~monk_tf.dev.Device`.
    """
    pass


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
        for c in self.conns:
            try:
                c.connect()
                c.login()
                return c.cmd(msg)
            except conn.ConnectionException as e:
                logger.exception("{}:{}:{}".format(
                    self.name,
                    c.name,
                    e
                ))
        # no connection was able to get to the return statement
        raise CantHandleException("dev:'{}',conns:'{}':couldn't send cmd '{}'".format(
            self.name,
            map(str, self.conns),
            msg,
        ))

    def __del__(self):
        # make sure all connections get closed on delete
        for c in self.conns:
            try:
                c.close()
            except Exception as e:
                logger.exception(e)
