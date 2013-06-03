#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MONK automated test framework serial connection handling
#
# Copyright (C) 2012 DResearch Fahrzeugelektronik GmbH
# Written and maintained by Thilo Fromm <fromm@dresearch-fe.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 2 of the License, or (at your option) any later version.
#


# disabling pylint messages:
# =========================
# Disabling message "Too many public methods": pylint: disable-msg=R0904
# Disabling message "Invalid name" (CamelCase) pylint: disable-msg=C0103
# Disabling message "use of global" pylint: disable-msg=W0603

""" Package for the Serial Connection Threading classes 

There are two thread classes. One for reading from serial interface and one for 
writing on serial interface. Every of this threads have a queue buffer.
"""

import collections
import time
import threading
import logging
import sys
import serial


class Thread_serial_read(threading.Thread):
    """thread for read access handling
    """
    count = 0
    
    
    def __init__(self, father, connection):
        threading.Thread.__init__(self)
        self.father_thread = father

        self.buffer_lock = threading.Lock()
        self.readbuffer =  collections.deque()
        self.conn = connection
        self.logread = ""
        Thread_serial_read.count = Thread_serial_read.count + 1
        self.count = Thread_serial_read.count
    
    def _read(self):
        """internal read
        
        read till you get a char or die
        """
        oldt = self.conn.timeout
        self.conn.timeout = 1
        ret = ""
        try:
            ret = serial.Serial.read(self.conn)
        except Exception as e:
            logging.warn('Exception error is: %s' % e)
            ret = ""
            time.sleep(0.25)
        self.conn.timeout = oldt
        return ret
    
    def read(self, size=1):
        self.buffer_lock.acquire()
        if len(self.readbuffer) > 0:
            ret = self.readbuffer.popleft()
        else:
            ret = ""
        self.buffer_lock.release()
        return ret

    def flush(self):
        while len(self.readbuffer) > 0:
            self.readbuffer.popleft()

    def run(self):
        """ thread loop
        
        actions:
        - read all connections
        - wait short while
        """
        while True:
            ret = self._read()
            if not ret is "":
                if ret == '\n':
                    logging.info("read" + str(self.count) + "<" + 
                                    str(self.logread) + ">")
                    self.logread = ""
                else:
                    self.logread = self.logread + ret
                    
#                single character logging
#                logging.info("read" + str(self.count) + "<" + 
#                                    str(ret) + ">")

                self.buffer_lock.acquire()
                self.readbuffer.append(ret)
                self.buffer_lock.release()
            if not self.father_thread.is_alive():
                logging.info("Farit! Stopp It!")       
                self.conn.close()               
                sys.exit()            
