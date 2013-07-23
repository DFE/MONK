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

import os
import time
import logging

import serial

class SerialIO(serial.Serial):
    """ console like interface on top of pyserial

    The job of this class is to allow a console like input-output behaviour
    between the user of this class and a serial interface. To achieve this some
    abstraction layers are necessary.
    """


    def __init__(self, *args, **kwargs):
        """
        :param prompt: set a prompt for the communication
        """
        print "wrong init :("
        self._logger = logging.getLogger(__name__)
        if "linesep" in args:
            self.linesep = args["linesep"]
            args.pop("linesep")
        super(SerialIO,self).__init__(*args, **kwargs)


    def cmd(self, msg):
        """ send a command and receive it's output

        :param msg: the command that shall be sent, with or without line
                    separator in the end
        :return: the output of the command as created by target device
        """
        # a command will only be executed, if it ends in a linebreak
        self.write(msg.strip() + self.linesep)
        # remove first line (the cmd itself), last line (the next prompt)
        # and unnecesary \r characters from the output
        return self.linesep.join(self.readall().replace("\r","").split("\n")[1:-1])

    @property
    def linesep(self):
        """ In most cases ``os.linesep``.
        """
        try:
            return self._linesep
        except AttributeError:
            self.linesep = os.linesep
            return self._linesep

    @linesep.setter
    def linesep(self, lsep):
        self._linesep = lsep
