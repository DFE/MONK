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

class SerialConsole(serial.Serial):
    """ console like interface on top of pyserial

    The job of this class is to allow a console like input-output behaviour
    between the user of this class and a serial interface. To achieve this some
    abstraction layers are necessary.
    """

    _DEFAULT_PROMPT=">>> "

    class ReadState:
        LEFT_OVER=1
        FOUND_START=2

    def __init__(self, *args, **kwargs):
        """
        :param prompt: set a prompt for the communication
        """
        self._logger = logging.getLogger(__name__)
        self.prompt = Serial._DEFAULT_PROMPT
        if args:
            self.prompt = prompt
        super(Serial,self).__init__(*args, **kwargs)


    def cmd(self, msg, prompt=None, sleep_length=.1, timeout=5, linesep="\n"):
        """ send a command and retrieve it's response.

        Text that might be in the buffer before the command is ignored, as well
        as text beginning from the prompt after the command. The command text
        itself and the prompt afterwards are the borders of the command output,
        that is returned.

        The basic structure of a command is like that::

            <something left in the buffer><our command><EOL>
            <command output><EOL> # optional (EOLs inside the command output are treated as any character)
            <prompt><space>

        We try to just grab the ``<command output>`` and return it.

        .. note:: The results from the last output can be optained with the
        attributes ``last_cmd``, ``last_confidence`` and ``last_output``.

        :param msg: the shell command you want to execute over the serial line.

        :param prompt: the prompt that signals that a command is treated and
                       the next command can be sent. If None, the object's
                       default is used and if that is also not set the default
                       python prompt is used: ``>>> ``.

        :param sleep_length: defines how long the process should sleep until
                             the next iteration of the loop is started.

        :param timeout: defines in seconds how long this method should take at
                        most.

        :param linesep: the line separator used for the communication. It
                        defaults to ``\n``

        :param return: the command output.
        """
        # prepare
        cmd = msg.strip() + linesep
        self.write(cmd)
        self.__last_cmd = cmd
        self.__last_confidence, self.__last_output =  self.read_until(
                cmd,prompt, sleep_length, timeout)
        return self.last_output


    def read_until(self, end_strip, start_strip=None, sleep_length=.1, timeout=5):
        """ read until end strip found

        This function reads everything available in the buffer, then waits
        ``sleep_length`` seconds and then starts again, either until it finds
        ``end_strip`` in the buffered text or the ``timeout`` runs out.
        Everything will be deleted, beginning from the ``end_strip``, because
        that is expected to be knowledge the user already has.
        
        The same way as ``end_strip`` works on the end, you can also define a
        ``start_strip``, which will delete everything in the buffer until the
        start_strip is found.

        :param end_strip: The text which terminates the search. A string as
        excepted by :py:func:`str.find`.

        :param start_strip: The text which starts the search. A string as
        expected by :py:func:`str.find`.

        :param sleep_length: defines how long the process should sleep until
                             the next iteration of the loop is started.

        :param timeout: defines in seconds how long this method should take at
                        most.

        :return: (boolean, string) - The first param is True as long as the
                 timeout didn't deplete. The second param contains the output
                 as far as it was received.
        """
        state = ReadState.LEFT_OVER if start_strip else ReadState.FOUND_START
        out = ""
        start_time = time.time()
        while True:
            if time.time() - start_time >= timeout:
                self.__last_confidence = False
                self.__last_cmd = msg
                self.__last_output = out
                return out
            time.sleep(sleep_length)
            out += self.read(self.inWaiting())
            if state == ReadState.LEFT_OVER:
                pos = out.find(start_strip)
                if pos >= 0:
                    # forget everything up to including the start_strip
                    out = out[pos+len(start_strip):]
                    state = ReadState.FOUND_START
            elif state == ReadState.FOUND_START:
                pos = out.find(end_strip)
                if pos >= 0:
                    # strip the end_strip and everything afterwards
                    out = out[:pos]
                    return True, out



    @property
    def prompt(self):
        try:
            return self.__prompt
        except AttributeError:
            return None


    @prompt.setter
    def prompt(self,new_prompt):
        self.__prompt = new_prompt


    @property
    def last_confidence(self):
        try:
            return self.__last_confidence
        except AttributeError:
            return None


    @property
    def last_cmd(self):
        try:
            return self.__last_cmd
        except AttributeError:
            return None


    @property
    def last_output(self):
        try:
            return self.__last_output
        except AttributeError:
            return None
