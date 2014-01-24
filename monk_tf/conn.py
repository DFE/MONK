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

This module implements the lowest layer of interaction with a
:term:`target device`, the connection layer. This means that you can use this
module to create :py:class:`~monk_tf.conn.AConnection` objects, interact with
them, and manipulate their internal states.

States are implemented based on the State design pattern via
:py:class:`~monk_tf.conn.AState`. Connection objects hold a
:py:attr:`~monk_tf.conn.AConnection.current_state` attribute. Every time a
public method of a connection is called, the object will forward this call
to its :py:attr:`~monk_tf.conn.AConnection.current_state`, which will
then execute the method depending on what the task of the state is.

As an Example, let's take a :py:class:`~monk_tf.conn.SerialConnection`. If you
execute its :py:meth:`~monk_tf.conn.AConnection.connect` method, the connection
will delegate this task to its
:py:attr:`~monk_tf.conn.AConnection.current_state` which is probably a
:py:class:`~monk_tf.conn.Disconnected` object but might be any other state as
well. Each State object also has a method for each public
:py:class:`~monk_tf.conn.AConnection` method, e.g.,
:py:meth:`~monk_tf.conn.Disconnected.connect`, which makes it clear which
:py:class:`~monk_tf.conn.AState` method will be called from the
:py:class:`~monk_tf.conn.AConnection`. In this
:py:class:`~monk_tf.conn.AConnection` method there might be some checks (not in
this case, though) and then it will redirect the task to a private method of
:py:class:`~monk_tf.conn.SerialConnection`, in this case
:py:meth:`~monk_tf.conn.SerialConnection._connect`. Because this private method
expects that all checks are done it will attempt to initiate the connection.

This does not just seem complicated, it actually is. The reason is that the
State design pattern was applied here. To wrap your head around the idea might
be complicated at first but it also comes with great payoff. For example, when
you write a new child class of :py:class:`~monk_tf.conn.AConnection` you
overwrite the methods :py:meth:`~monk_tf.conn.AConnection._connect`,
:py:meth:`~monk_tf.conn.AConnection._login`,
:py:meth:`~monk_tf.conn.AConnection._cmd`, and
:py:meth:`~monk_tf.conn.AConnection._disconnect` to show how your connection
handles the different events. Because the State design pattern was chosen you
do not have to worry about checking if the connection is really ready for what
you want to do in this event, e.g., in
:py:meth:`~monk_tf.conn.AConnection._cmd` you do not need to worry if you are
already connected or not, because this has already been asserted by
:py:class:`~monk_tf.conn.AConnection` and the State design pattern. You can
expect to have a direct connection to the :term:`target device` and can start
writing the code that is necessary to send a :term:`shell command` to the
device.

Something else that might be confusing about this layer is that many methods
have undefined return behaviour. This is a disadvantage and a feature of Python
at the same time, because in Python there is no way to ensure that a method
only returns some specific type or result. Here we use it as a feature, because
from private methods like :py:meth:`~monk_tf.conn.AConnection._login` that
you implement in individual :py:class:`~monk_tf.conn.AConnection` child classes,
you can be sure that your return results get delivered to the publicly called
:py:meth:`~monk_tf.conn.AConnection.login`. And because Python does not force
us to define a specific return result you can choose in your private methods if
you want to return something and if so what it might be. In
:py:class:`~monk_tf.conn.SerialConnection` we decided to not return anything.
Therefore anybody who might decide to check what gets returned basically just
reads``None`` as the result and that is fine.

The code of this module is split into the following parts:
    1. *Exceptions* - all exceptions that are used in this module
    2. *AConnection* - the abstract connection class which all other
       connections are based on
    3. *Test Connections* - a list of connections that do not really connect to
       a :term:`target device` but instead are used for debugging purposes of
       your test cases
    4. *Real Connections* - the real connections that connect MONK to a
       :term:`target device`
    5. *AState* - the abstract State class which all other states are based on
    6. *State Classes* - the implementation of the state machine

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
    """ is the base class for exceptions of this package.
    """
    pass

class NotConnectedException(ConnectionException):
    """ is raised when connection has not been established yet.
    """
    pass

class AuthenticationRequiredException(ConnectionException):
    """ is raised when user has not been authenticated yet.
    """
    pass

class MockConnectionException(ConnectionException):
    """ is a mock exception that can be used in test scenarios.
    """
    pass

class UnexpectedPromptException(ConnectionException):
    """ is raised when the last prompt was not what was expected.
    """
    pass

class CommandException(ConnectionException):
    """ is raised when there was an unidentified problem while executing a command.
    """
    pass

class EmptyResponseException(ConnectionException):
    """ is raised when sending a command resulted in no response.
    """
    pass

class CantConnectException(ConnectionException):
    """ is raised if a connection cannot be established.

    Reasons might be that the physical connection is not established or that
    the executing user lacks privileges to use this connection, e.g., when he
    is not in the *dialout* group on a Linux machine.
    """
    pass


##########################################
#
# Connections - Connect to a target device
#
#########################################

class AConnection(object):
    """ Abstract base class for other connections to extend.

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

        :param start_state: the :py:class:`~monk_tf.conn.AState` object the
                            connection should start in.

        :param name: a name to distinguish the connection from others. This is
                     mostly used for :py:mod:`logging` output.

        :param user_prompt: the prompt that requests the login username.

        :param pw_prompt: the prompt that requests the login password.

        :param credentials: login credentials as needed by the corresponding
                            connection type, e.g.,
                            :py:class:`~monk_tf.conn.SerialConnection`.

        :param linesep: the line separator used in shell commands. This depends
                        mostly on your TermIOs configuration and the
                        :term:`target device`.
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
        """ Initiate connection with :term:`target device`.

        :return: what the connection implemented. May be None.
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
        """ Authenticate to :term:`target device`.

        It uses a tupel of ``(user, password)`` that is expected to be found in
        an attribute ``credentials``. If there are no ``credentials`` then it
        is assumed that a login is not necessary and nothing happens.

        :return: what the connection implemented. May be None.
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
        """ Send :term:`shell command` to :term:`target device`.

        :param msg: the :term:`shell command`

        :return: what the connection implemented. May be None.
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
        """ Deactivate the connection to :term:`target device`.

        :return: what the connection implemented. May be None.
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

    def can_login(self):
        """ Checks wether the prompt is one of the login prompts.

        :return: True if a login prompt or False otherwise.
        """
        return any(self.last_prompt.endswith(p) for p in (
                        self.pw_prompt,
                        self.user_prompt,))

    def _prompt(self):
        """ Request a prompt.

        This is like hitting the Return button in a shell session.

        :return: the new prompt and any response returned by the
                 :term:`target system`.
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
    """ Return everything sent to this connection.
    """

    def __init__(self, *args, **kwargs):
        self.logged_in = kwargs.pop("logged_in", False)
        super(EchoConnection, self).__init__(*args, **kwargs)

    def _connect(self):
        pass

    def _login(self):
        self.logged_in = True

    def _cmd(self, msg, *args, **kwargs):
        return msg

    def _disconnect(self):
        pass


class DefectiveConnection(AConnection):
    """ Raise a :py:class:`~monk_tf.conn.MockConnectionException` on each call.
    """

    def _connect(self):
        raise MockConnectionException()

    def _login(self):
        raise MockConnectionException()

    def _cmd(self, msg, *args, **kwargs):
        raise MockConnectionException()

    def _disconnect(self):
        raise MockConnectionException()


###############################################
#
# Real Connections - Connect to a target device
#
###############################################

class SerialConnection(AConnection):
    """ Connect to :term:`target device` via serial interface.
    """

    def __init__(self,
            serial_class=None,
            *args, **kwargs):
        """

        With this class you can use all params from
        :py:class:`~monk_tf.conn.AConnection` and additionally:

        :param serial_class: the class that provides the serial interface.
        """
        self.serial_class = serial_class if serial_class else serial.Serial
        kwargs["port"] = kwargs.get("port", "/dev/ttyUSB1")
        kwargs["baudrate"] = int(kwargs.get("baudrate", 115200))
        kwargs["timeout"] = float(kwargs.get("timeout", 1.5))
        if "user" in kwargs and "password" in kwargs and not "credentials" in kwargs:
            kwargs["credentials"] = (kwargs.pop("user"), kwargs.pop("password"))
        super(SerialConnection, self).__init__(*args, **kwargs)

    def _connect(self):
        try:
            self._serial = self.serial_class(*self._args, **self._kwargs)
        except OSError as e:
            self._logger.exception(e)
            raise CantConnectException("Check cables and user rights!")

    def _login(self):
        self._cmd(self.credentials[0], returncode=False)
        if not self.last_prompt.endswith(self.pw_prompt):
            raise UnexpectedPromptException(
                "'{}'.endswith('{}')".format(self.last_prompt, self.pw_prompt))
        self._cmd(self.credentials[1], returncode=False)
        if self.can_login():
            raise UnexpectedPromptException(
                "login should be finished but prompt is '{}'".format(
                    self.last_prompt))

    def _cmd(self,msg, returncode=True, expected_output=True):
        """ Unsafe, direct command interface.

        Also updates :py:attr:`last_cmd`, :py:attr:`last_prompt` and
        :py:attr:`last_out`.

        :param msg: the :term:`shell command` to be executed remotely.

        :param returncode: want a returncode? otherwise non is requested from
                           :term:`target device`

        :param expected_output: is an output expected? True might result in an
                                :py:class:`~monk_tf.conn.EmptyResponseException`

        :return: the standard output from the command execution
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
    """ The abstract base class for all connection related states to extend.

    An AState is a representation of a set of reactions in a specific state.
    Therefore it does not make sense to keep a lot of stateful information in a
    single AState object. This makes creation of multiple AState objects of the
    same type unnecessary, which is why this class makes sure that all its
    child classes can only have a single instance. This design pattern is
    called Singleton.
    """

    _CONNECT = "CONNECT"
    _LOGIN = "LOGIN"
    _CMD = "CMD"
    _DISCONNECT= "DISCONNECT"
    _LOGGED_OUT = "LOGGED_OUT"

    def __new__(cls, *args, **kwargs):
        """ Implement Singleton as default object creation of this class.
        """
        try:
            return cls._instance
        except AttributeError:
            cls._instance = super(AState, cls).__new__(cls, *args, **kwargs)
            return cls._instance

    def next_state(self, connection):
        """ State transition table. Must be overwritten by child classes.
        """
        logger.warning("{}: class does not overwrite next_state() method".format(
            self.__class__.__name__))
        return self

    def __str__(self):
        """ Represent a state by its class name.
        """
        return self.__class__.__name__


class Disconnected(AState):
    """ Defines interaction if connection has not been established yet.
    """

    def connect(self, connection):
        """ Initiate connection with :term:`target device`.

        :param connection: the connection that uses this state
        :return: what the connection implemented. May be None.
        """
        self.event = self._CONNECT
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        return connection._connect()

    def login(self, connection):
        """ Should not be called because there is no connection.
        """
        self.event = self._LOGIN
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        raise NotConnectedException()

    def cmd(self, connection, msg):
        """ Should not be called because there is no connection.
        """
        self.event = self._CMD
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        raise NotConnectedException()

    def disconnect(self, connection):
        """ Does not do anything because we are already disconnected.
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
        """ Does nothing because we are already connected.
        """
        self.event = self._CONNECT
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        connection._logger.warning("tried to connect but is already connected")

    def login(self, connection):
        """ Authenticates at connection, if object has credentials.

        :param connection: the connection that uses this state.
        :return: the result of the login. May be None. If False then the
                 connection object has no credentials to use. This
                 may indicate a problem but may also mean that no login
                 is necessary.
        """
        self.event = self._LOGIN
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        if hasattr(connection, "credentials") and connection.credentials:
            connection._logger.debug("authenticate for user '{}'"
                    .format(connection.credentials[0]))
            # make sure you are ready to login
            if connection.can_login():
                connection._prompt()
            try:
                # here check again and only login if not already logged in!
                # same check as before
                if connection.can_login():
                    out = connection._login()
            except ConnectionException as e:
                self.event = self._LOGGED_OUT
                raise type(e), type(e)(e.message), sys.exc_info()[2]
        else:
            connection._logger.warning("no creds -> no login")
            return False

    def cmd(self, connection, msg):
        """ Sends a command if login not necessary, otherwise raises exception

        :param connection: the connection that uses this state.
        :param msg: the shell command to be sent via the connection.
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
        """ Deactivates the connection.

        :param connection: the connection that uses this state.
        :return: the disconnection result from the connection. May be None.
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
        """ Does nothing because we are already connected.

        :param connection: the connection that uses this state.
        """
        self.event = self._CMD
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        connection._logger.warning("already connected")

    def login(self, connection):
        """ Does nothing, because we are already logged in.

        :param connection: the connection that uses this state.
        """
        self.event = self._LOGGED_OUT
        connection._logger.debug("execute event '{}' in state '{}'".format(
            self.event,
            str(self),
        ))
        connection._logger.warning("already logged in")

    def cmd(self, connection, msg):
        """ Send a shell command to :term:`target device`

        :param connection: the connection that uses this state.
        :param msg: the shell command to be sent.
        :return: the standard output of the shell command.
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
        """ Closes the connection.

        :param connection: the connection that uses this state.
        :return: the disconnect result from the connection. May be None.
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
