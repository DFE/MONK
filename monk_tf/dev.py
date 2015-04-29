# -*- coding: utf-8 -*-
#
# MONK automated test framework
#
# Copyright (C) 2013, 2014, 2015 DResearch Fahrzeugelektronik GmbH
# Written and maintained by MONK Developers <project-monk@dresearch-fe.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 3 of the License, or (at your option) any later version.
#

"""
This module implements device handling. Using the classes from this module you
can abstract a complete :term:`target device` in a single object. On
instantiation you give it some connections and then (theoretically) let the
device handle the rest.

Example:

.. code-block:: python

    import monk_tf.dev as md
    import monk_tf.conn as mc
    # create a device with a ssh connection and a serial connection
    d=md.Device(
        mc.SshConn('192.168.2.100', 'tester', 'secret'),
        mc.SerialConn('/dev/ttyUSB2', 'root', 'muchmoresecret'),
    )
    # send a command (the same way as with connections)
    return_code, output = d.cmd('ls -al')
    print output
    [...]
"""

import logging
import time
import json

import requests
import pexpect

import monk_tf.general_purpose as gp
import monk_tf.conn

logger = logging.getLogger(__name__)

############
#
# Exceptions
#
############

class ADeviceException(gp.MonkException):
    """ Base class for exceptions of the device layer.
    """
    pass

class UpdateFailedException(ADeviceException):
    """ is raised if an update didn't get finished or was rolled back.
    """
    pass

class WrongNameException(ADeviceException):
    """ is raised when no connection with a given name could be found.
    """
    pass


##############################
#
# Devices - currently just one
#
##############################

class Device(gp.MonkObject):
    """ is the API abstraction of a :term:`target device`.
    """

    def __init__(self, *args, **kwargs):
        """
        :param conns: list of connections. The following works as well::

            ``Device(OneConnection(...), AnotherConnection(...),...)``

        :param name: Device name for logging purposes.
        """
        super(Device, self).__init__(
                name=kwargs.pop("name",None),
                module=__name__,
        )
        use_conns = kwargs.pop("use_conns", [])
        self.use_conns = [use_conns] if isinstance(use_conns, str) else [cname.strip() for cname in use_conns if cname]
        self.conns = kwargs.pop("conns", {})
        self.prompt = PromptReplacement()

    @property
    def firstconn(self):
        return self.conns.get(self.use_conns[0])

    def cmd(self, msg, expect=None, timeout=30, login_timeout=None,
            do_retcode=True, conn=None):
        """ Send a :term:`shell command` to the :term:`target device`.

        :param msg: the :term:`shell command`.

        :param expect: if you don't expect a prompt in the end but something
                       else, you can add a regex here.

        :param timeout: when command should return without finding what it's
                        looking for in the output. Will raise a
                        :py:exception:`pexpect.Timeout` Exception.

        :param do_retcode: should this command retreive a returncode

        :param conn: the name of the connection that should be used for this
                     command.

        :return: :term:`returncode`, :term:`standard output` of the shell command
        """
        self.log("cmd({},{},{},{},{})".format(
            msg, expect, timeout, login_timeout, do_retcode))
        if not self.conns:
            self._logger.warning("device has no connections to use for interaction")
        connection = conn or self.conns[self.use_conns[0]]
        self.log("send cmd '{}' via connection '{}'".format(
            msg,
            connection,
        ))
        return connection.cmd(
                msg=msg,
                expect=PromptReplacement.replace(connection, expect),
                timeout=timeout,
                do_retcode=do_retcode,
        )

    def cp(self, src_path, trgt_path):
        """ send files via scp to target device

        :param src_path: the path to the file on the host machine
        :param trgt_path: the path of the file on the target machine
        """
        self.log("send file from {} to {} on the target device".format(
            src_path,
            trgt_path,
        ))
        self.conns.get("ssh1").cp(src_path, trgt_path)
        self.log("sending file succeeded")

    def close_all(self):
        """ loop through all connections calling :py:meth:`~monk_tf.conn.ConnectionBase.close`.
        """
        self.log("close_all()")
        for c in self.conns.values():
            c.close()

    def __str__(self):
        return "{}({}):name={}".format(
                self.__class__.__name__,
                [str(c) for c in self.conns],
                self.name,
        )

#########
#
# Helpers
#
#########

class PromptReplacement(object):
    """ should be replaced by each connection's own prompt.
    """
    @classmethod
    def replace(cls, c, expect):
        """ this is an awful workaround...
        """
        if not expect:
            return expect
        if isinstance(expect, str):
            return expect
        if isinstance(expect, Exception):
            return expect
        if not isinstance(expect, list):
            expect = list(expect)
        return [c.prompt if isinstance(e, PromptReplacement) else e for e in expect]
