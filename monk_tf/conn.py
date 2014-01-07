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

""" Connection Layer

Implements the lowest layer of interaction with a :term:`target device`. This
means that you can use this module to create connections, interact with them
and manipulate their internal states.

States are implemented with the State design pattern. Connection objects hold a
current_state attribute. Everytime a public method of a connection is called,
the object will forward that message to its current_state and the state will
then execute the method depending on what the task of the state is.

The code is split into the following parts:
    1. *Exceptions* - all exceptions that are used in this module
    2. *AConnection* - the abstract Connection class which all other
       connections are based on.
    3. *Test Connections* - a list of connections that do not really connect to
       a :term:`target device` but instead are used for debugging purposes of
       your test cases.
    4. *Real Connections* - the real connections that connect MONK to a
       :term:`target device`.
    4. *AState* - the abstract State class which all other states are based on.
    5. *State Classes* - the implementation of the state machine.
"""

import os
import sys
import logging

import serial

logger = logging.getLogger(__name__)

############
#
# Exceptions
#
############

class ConnectionException(Exception):
    """ baseclass for exceptions of this package
    """
    pass

class NotConnectedException(ConnectionException):
    """ connection is not established, yet
    """
    pass

class AuthenticationRequiredException(ConnectionException):
    """ user is not authenticated, yet
    """
    pass

class MockConnectionException(ConnectionException):
    """ a mock exception that can be used in test scenarios
    """
    pass

class UnexpectedPromptException(ConnectionException):
    """ the last prompt was not what was expected
    """
    pass

class CommandException(ConnectionException):
    """ there was an unidentified problem while executing a cmd
    """
    pass

class EmptyResponseException(ConnectionException):
    """ sending a command resulted in no response
    """
    pass


##########################################
#
# Connections - Connect to a target device
#
#########################################

class AConnection(object):
    """ abstract base class for other connections to extend.

    This class preimplements the interaction between a
    :py:class:`~monk_tf.conn.AConnection` and its
    :py:class:`~monk_tf.conn.AState`.
    """

    def __init__(self,
            start_state=None,
            name=None,
            user_prompt="login: ",
            pw_prompt="Password: ",
            credentials=None,
            linesep=None,
            *args, **kwargs):
        """
        :param start_state: the state the connection should start in
        :param name: a name to differentiate the connecton from others
        :param user_prompt: the prompt that requests the login username.
        :param pw_prompt: the prompt that requests the login password.
        :param credentials: login credentials as needed by the corresponding
                            connection
        :param linesep: the line separator used in shell commands.
        """
        self.current_state = start_state if start_state else Disconnected()
        self.name = name if name else self.__class__.__name__
        self.user_prompt = user_prompt
        self.pw_prompt = pw_prompt
        self.credentials = credentials
        self.linesep = linesep if linesep else os.linesep
        # store the remaining args for later usage
        self._args = args
        self._kwargs = kwargs
        self._logger = logging.getLogger("{}:{}".format(__name__, self.name))
        self._logger.debug("initialized with start_state '{}'".format(
            str(self.current_state),
        ))
        self.last_prompt = ""
        self.last_out = ""
        self.last_cmd = ""

    def connect(self):
        """ initiate connection with :term:`target device`

        :return: whatever the current state might return. Might be None.
        """
        self._logger.info("connecting...")
        try:
            out = self.current_state.connect(self)
        except Exception as e:
            raise type(e), type(e)(e.message), sys.exc_info()[2]
        finally:
            self.current_state = self.current_state.next_state(self)
            self._logger.debug("current state '{}'".format(self.current_state))
        return out

    def login(self):
        """ authenticate to :term:`target device`

        It uses a tupel of ``(user, password)`` that is hopefully stored in an
        attribute ``credentials``.

        :return: whatever the current state might return. Might be None.
        """
        self._logger.info("authenticating...")
        try:
            out = self.current_state.login(self)
        except Exception as e:
            raise type(e), type(e)(e.message), sys.exc_info()[2]
        finally:
            self.current_state = self.current_state.next_state(self)
            self._logger.debug("current state '{}'".format(self.current_state))
        return out

    def cmd(self, msg):
        """ send :term:`shell command` to :term:`target device`

        :param msg: the :term:`shell command`
        :return: the standard output of the :term:`shell command`.
        """
        self._logger.info("sending cmd '{}'".format(msg))
        try:
            out = self.current_state.cmd(self, msg)
        except Exception as e:
            raise type(e), type(e)(e.message), sys.exc_info()[2]
        finally:
            self.current_state = self.current_state.next_state(self)
            self._logger.debug("current state '{}'".format(self.current_state))
        return out

    def disconnect(self):
        """ deactivate the connection to :term:`target device`

        :return: whatever the current state might return. Might be None.
        """
        self._logger.info("logging out...")
        try:
            out = self.current_state.disconnect(self)
        except Exception as e:
            raise type(e), type(e)(e.message), sys.exc_info()[2]
        finally:
            self.current_state = self.current_state.next_state(self)
            self._logger.debug("current state '{}'".format(self.current_state))
        return out

    def _prompt(self):
        """ request a prompt.

        This is like hitting the Return button in a shell session
        :return: the new prompt and whatever the :term:`target system` wants to
                 respond.
        """
        self._logger.info("requesting new prompt")
        return self._cmd("",returncode=False) + os.linesep + self.last_prompt

    def __str__(self):
        return "{}:({})".format(self.__class__.__name__, str({
            '_args':[str(a) for a in self._args],
            '_kwargs': self._kwargs,
            'current_state' : str(self.current_state),
            'name' : self.name,
        }))


###################################################
#
# Test Connections - Fake Connections for Debugging
#
###################################################

class EchoConnection(AConnection):
    """ return everything sent to this connection; for debugging
    """

    def __init__(self, *args, **kwargs):
        self.logged_in = kwargs.pop("logged_in", False)
        super(EchoConnection, self).__init__(*args, **kwargs)

    def _connect(self):
        pass

    def _login(self):
        self.logged_in = True

    def _cmd(self, msg):
        return msg

    def _disconnect(self):
        pass


class DefectiveConnection(AConnection):
    """ raise a MockConnectionException on each call
    """

    def _connect(self):
        raise MockConnectionException()

    def _login(self):
        raise MockConnectionException()

    def _cmd(self, msg):
        raise MockConnectionException()

    def _disconnect(self):
        raise MockConnectionException()


###############################################
#
# Real Connections - Connect to a target device
#
###############################################

class SerialConnection(AConnection):
    """ connect to :term:`target device` via serial interface
    """

    def __init__(self,
            serial_class=None,
            *args, **kwargs):
        """
        :param serial_class: the class that provides the serial interace.
        """
        self.serial_class = serial_class if serial_class else serial.Serial
        super(SerialConnection, self).__init__(*args, **kwargs)

    def _connect(self):
        self._serial = self.serial_class(*self._args, **self._kwargs)

    def _login(self):
        self._cmd(self.credentials[0], returncode=False)
        if not self.last_prompt.endswith(self.pw_prompt):
            raise UnexpectedPromptException(
                "'{}'.endswith('{}')".format(self.last_prompt, self.pw_prompt))
        self._cmd(self.credentials[1], returncode=False)
        if any(self.last_prompt.endswith(p) for p in (
                self.pw_prompt,
                self.user_prompt,)):
            raise UnexpectedPromptException(
                "login should be finished but prompt is '{}'".format(
                    self.last_prompt))

    def _cmd(self,msg, returncode=True, expected_output=True):
        """ unsafe, direct command interface.

        Also updates :py:attr:`last_cmd`, :py:attr:`last_prompt` and
        :py:attr:`last_out`.

        :param msg: the :term:`shell command` that should be executed remotely.
        :param returncode: if a returncode should be checked or not
        :param expected_output: is an output expected?
        :return: the standardoutput from the command execution
        """
        stripped = msg.strip()
        msg_rcd = stripped + ("; echo \"$?\"" if stripped and returncode else "")
        # command will only be executed, if it ends in a linebreak
        msg_sepd = msg_rcd + self.linesep
        self._serial.write(msg_sepd)
        # read all that comes back
        out = self._serial.readall()
        if not out:
            # try again
            out = self._serial.readall()
            if not out and expected_output:
                raise EmptyResponseException()
        out_repl = out.replace("\r","")
        # return without msg and prompt
        lines = out.split("\n")
        self.last_cmd = msg
        self.last_prompt = lines[-1]
        # if there is no returncode line, it doesn't need to be removed
        remove = -2 if returncode and len(lines) >= 2 else -1
        self.last_out = os.linesep.join(lines[1:remove])
        try:
            self.last_returncode = int(lines[remove])
        except ValueError:
            # returncode couldn't be retrieved
            # happens if e.g. returncode=False or login is necessary
            self.last_returncode = 0
        return self.last_out

    def _disconnect(self):
        try:
            self._serial.close()
            del self._serial
        except AttributeError:
            pass


#########################################################
#
# State Classes - A State Machine as State Design Pattern
#
#########################################################

class AState(object):
    """ the abstract base class for all connection related states to extend.

    An AState is a representation of a set of reactions in a specific state.
    Therefore it does not make sense to keep a lot of stateful information in a
    single AState object. This makes creation of many AState objects of the
    same type unnecessary, which is why this class makes sure that all it's
    child classes can only have a single implementation. This design pattern is
    called Singleton.
    """

    _CONNECT = "CONNECT"
    _LOGIN = "LOGIN"
    _CMD = "CMD"
    _DISCONNECT= "DISCONNECT"
    _LOGGED_OUT = "LOGGED_OUT"

    def __new__(cls, *args, **kwargs):
        """ implement Singleton as default object creation of this class.
        """
        try:
            return cls._instance
        except AttributeError:
            cls._instance = super(AState, cls).__new__(cls, *args, **kwargs)
            return cls._instance

    def next_state(self, connection):
        """ state transition table. Must be overwritten by child classes
        """
        logger.warning("{}: class does not overwrite next_state() method".format(
            self.__class__.__name__))
        return self

    def __str__(self):
        """ represent a state by its class name
        """
        return self.__class__.__name__


class Disconnected(AState):
    """ Defines interaction if connection is not established yet.
    """

    def connect(self, connection):
        """ initiate connection with :term:`target device`

        :param connection: the connection that uses this state
        :return: depends on what the connection's protected :py:meth:`_connect`
                 method returns. Could be None.
        """
        self.event = self._CONNECT
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        return connection._connect()

    def login(self, connection):
        """ should not be called, because not connected
        """
        self.event = self._LOGIN
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        raise NotConnectedException()

    def cmd(self, connection, msg):
        """ should not be called, because not connected
        """
        self.event = self._CMD
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        raise NotConnectedException()

    def disconnect(self, connection):
        """ does not do anything, because already disconnected
        """
        self.event = self._DISCONNECT
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        logger.warning("{}: tried to disconnect but is already disconnected"
                .format(connection.name))

    def next_state(self, connection):
        if self.event == self._CONNECT:
            return Connected()
        else:
            return self


class Connected(AState):
    """ Defines interaction if unauthenticated connection is established.
    """

    def connect(self, connection):
        """ does nothing, because already connected
        """
        self.event = self._CONNECT
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        connection._logger.warning("tried to connect but is already connected")

    def login(self, connection):
        """ authenticates at connection, if object has credentials

        :param connection: the connection that uses this state.
        :return: the result of the login. Might be None. If False then the
                 connection object has no credentials that could be used. This
                 can mean that no login is necessary, though.
        """
        self.event = self._LOGIN
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        if hasattr(connection, "credentials"):
            connection._logger.debug("authenticate with credentials '{}'"
                    .format(connection.credentials))
            # make sure you are ready to login
            if any(connection.last_prompt.endswith(p) for p in (
                    connection.pw_prompt,
                    connection.user_prompt,)):
                connection._prompt()
            try:
                out = connection._login()
            except ConnectionException as e:
                self.event = self._LOGGED_OUT
                raise type(e), type(e)(e.message), sys.exc_info()[2]
        else:
            connection._logger.warning("no creds -> no login")
            return False

    def cmd(self, connection, msg):
        """ sends a command if login not necessary, otherwise raises Exception

        :param connection: the connection that uses this state.
        :param msg: the shell command that should be sent via the connection.
        :return: the standard output of the shell command.
        """
        self.event = self._CMD
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        connection._prompt()
        out = connection._cmd(msg)
        if connection.last_prompt.endswith(connection.pw_prompt):
            self.event = self._LOGGED_OUT
            raise AuthenticationRequiredException()

    def disconnect(self, connection):
        """ deactivates the connection.

        :param connection: the connection that uses this state.
        :return: the disconnection result. Might be None.
        """
        self.event = self._DISCONNECT
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        connection._logger.info("disconnecting")
        return connection._disconnect()

    def next_state(self, connection):
        if self.event == self._DISCONNECT:
            return Disconnected()
        elif self.event == self._LOGGED_OUT:
            return self
        elif self.event == self._CMD:
            return Authenticated()
        elif self.event == self._LOGIN:
            return Authenticated()
        else:
            return self


class Authenticated(AState):
    """ Defines interaction if connection is authenticated.
    """

    def connect(self, connection):
        """ does nothing, because already connected.

        :param connection: the connection that uses this state.
        """
        self.event = self._CMD
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        connection._logger.warning("already connected")

    def login(self, connection):
        """ does nothing, because already logged in.

        :param connection: the connection that uses this state.
        """
        self.event = self._LOGGED_OUT
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        connection._logger.warning("already logged in")

    def cmd(self, connection, msg):
        """ send a shell command to :term:`target device`

        :param connection: the connection that uses this state.
        :param msg: the shell command that should be transmitted.
        :return: the standard output of the sehll command.
        """
        self.event = self._CMD
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        out = connection._cmd(msg)
        if connection.last_prompt.endswith(connection.pw_prompt):
            self.event = self._LOGGED_OUT
            raise AuthenticationRequiredException()
        return out

    def disconnect(self, connection):
        """ closes the connection.

        :param connection: the connection that uses this state.
        :return: the disconnection result. Might be None.
        """
        self.event = self._DISCONNECT
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        return connection._disconnect()

    def next_state(self, connection):
        if self.event == self._DISCONNECT:
            return Disconnected()
        elif self.event == self._LOGGED_OUT:
            return Connected()
        elif self.event == self._CMD:
            # explicit > implicit
            return self
        else:
            return self
