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

"""
This module implements device handling. Using the classes from this module you
can abstract a complete :term:`target device` in a single object. On
instantiation you give it some connections and then (theoretically) let the
device handle the rest.

Example::

    import monk_tf.dev as md
    import monk_tf.conn as mc
    # create a device with a ssh connection and a serial connection
    d=md.Device(
        mc.SshConn('192.168.2.100', 'tester', 'secret'),
        mc.SerialConn('/dev/ttyUSB2', 'root', 'muchmoresecret'),
    )
    # send a command (the same way as with connections)
    print d.cmd('ls -al')
    [...]
"""

import logging
import time
import json

import requests
import pexpect

import conn

logger = logging.getLogger(__name__)

############
#
# Exceptions
#
############

class DeviceException(Exception):
    """ Base class for exceptions of the device layer.
    """
    pass

class CantHandleException(DeviceException):
    """ is raised when a request cannot be handled by the connections of a
    :py:class:`~monk_tf.dev.Device`.
    """
    pass

class UpdateFailedException(DeviceException):
    """ is raised if an update didn't get finished or was rolled back.
    """
    pass

class WrongNameException(DeviceException):
    """ is raised when no connection with a given name could be found.
    """
    pass


##############################
#
# Devices - currently just one
#
##############################

class Device(object):
    """ is the API abstraction of a :term:`target device`.
    """

    def __init__(self, *args, **kwargs):
        """
        :param conns: list of connections. The following works as well::

            ``Device(OneConnection(...), AnotherConnection(...),...)``

        :param name: Device name for logging purposes.
        """
        self._logger = logging.getLogger("Device")
        self.conns = kwargs.pop("conns", list(args))
        self._conns_dict = {}
        self.name = kwargs.pop("name", self.__class__.__name__)
        self.prompt = PromptReplacement()
        self._logger = logging.getLogger(self.name)

    def cmd(self, msg, expect=None, timeout=30, login_timeout=None, do_retcode=True):
        """ Send a :term:`shell command` to the :term:`target device`.

        :param msg: the :term:`shell command`.
        :param expect: if you don't expect a prompt in the end but something
                       else, you can add a regex here.
        :param timeout: when command should return without finding what it's
                        looking for in the output. Will raise a
                        :py:exception:`pexpect.Timeout` Exception.
        :param do_retcode: should this command retreive a returncode
        :return: the standard output of the :term:`shell command`.
        """
        self.log("cmd({},{},{},{},{})".format(
            msg, expect, timeout, login_timeout, do_retcode))
        if not self.conns:
            self._logger.warning("device has no connections to use for interaction")
        for connection in self.conns:
            try:
                self.log("send cmd '{}' via connection '{}'".format(
                    msg.encode('unicode-escape'),
                    connection,
                ))
                return connection.cmd(
                        msg=msg,
                        expect=PromptReplacement.replace(connection, expect),
                        timeout=timeout,
                        do_retcode=do_retcode,
                )
            except Exception as e:
                self._logger.exception(e)
        raise CantHandleException(
                "dev:'{}',conns:'{}':could not send cmd '{}'".format(
                    self.name,
                    map(str, self.conns),
                    msg,
        ))

    def get_conn(self, which):
        self.log("get_conn({})".format(which))
        try:
            return self.conns[which]
        except TypeError:
            try:
                return self._conns_dict[which]
            except KeyError:
                names = []
                for conn in self.conns:
                    if conn.name == which:
                        self.log("cache conn in dict:" + which)
                        self._conns_dict[which] = conn
                        return conn
                    else:
                        names.append(conn.name)
                raise WrongNameException("Couldn't retreive connection with name '{}'. Available names are: {}".format(which, names))

    def log(self, msg):
        """ sends a debug-level message to the logger

        This method is used so often, that a smaller version of it is quite
        comfortable.
        """
        self._logger.debug(msg)

    def close_all(self):
        self.log("close_all()")
        for c in self.conns:
            c.close()

    def __str__(self):
        return "{}({}):name={}".format(
                self.__class__.__name__,
                [str(c) for c in self.conns],
                self.name,
        )

class Hydra(Device):
    """ is the device type of DResearch Fahrzeugelektronik GmbH.
    """

    def update(self, link=None, force=None):
        """ update the device to current build from Jenkins.
        """
        self._logger.info("Attempt update to " + str(link or self._update_link))
        if not self.do_update:
            self.log("don't update due to MONK configuration")
            return
        connection_closed = (pexpect.EOF, pexpect.TIMEOUT)
        if not self.is_updated or force:
            _, out = self.cmd("do-update -c && get-update {} && do-update".format(
                    link if link else self._update_link,
                ), expect=("[lL]ogin: ",) +  connection_closed,
                timeout=600,
                do_retcode=False,
            )
            if self.conns[0].exp.after in connection_closed:
                self.log("reset connection after reboot")
                del self.conns[0]._exp
            self.log("wait till device recovered from updating")
            time.sleep(240)
            self.log("continue")
        else:
            self._logger.info("Already updated.")

    def __init__(self, *args, **kwargs):
        self._update_link = "http://hydraip-integration.internal.dresearch-fe.de:8080/view/HIPOS/job/HydraIP_UpdateV3_USB_Stick/lastSuccessfulBuild/artifact/rel-hudson/hyp-updateV3-hikirk.zip"
        self._jenkins_link = "http://hydraip-integration.internal.dresearch-fe.de:8080/view/HIPOS/job/daisy-hipos-dfe-closed-hikirk/api/json"
        # I want BOOLEANS!
        self.do_update = kwargs.pop("update",True) in ("True", True)
        self.do_resetconfig = kwargs.pop("resetconfig",True) in ("True", True)
        super(Hydra, self).__init__(*args, **kwargs)

    @property
    def latest_build(self):
        """ get the latest build ID from jenkins
        """
        out = requests.get(self._jenkins_link).text
        return json.loads(out)["lastSuccessfulBuild"]["number"]

    @property
    def current_fw_version(self):
        """ the current version of the installed firmware
        """
        _, out = self.cmd("do-update --current-update-version | awk '{print $2}'")
        return out

    @property
    def has_newest_firmware(self):
        """ check whether the installed firmware is the newest on jenkins
        """
        return str(self.latest_build) in str(self.current_fw_version)

    @property
    def is_updated(self):
        """ check whether the device is already updated.

        Currently it is implementd with
        :py:meth:`dev.Hydra.has_newest_firmware`.
        """
        return self.has_newest_firmware

    def reset_config(self):
        """ reset the HydraIP configuration on the device
        """
        if not self.do_resetconfig:
            self.log("don't reset config due to MONK configuration")
            return
        # otherwise it might not really be a reset
        self.cmd("rm /etc/drconfig/hydraip.json.good")
        self.cmd(
            msg="rm -rf /var/lib/connman/* && hip-activate-config --reset && sync && halt -p",
            expect=[self.prompt, pexpect.EOF, pexpect.TIMEOUT],
            do_retcode=False,
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
