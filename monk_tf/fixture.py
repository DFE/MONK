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
Instead of creating :py:class:`~monk_tf.dev.Device` and
:py:class:`~monk_tf.conn.AConnection` objects by yourself, you can also choose
to put corresponding data in a separate file and let this layer handle the
object concstruction and destruction for you. Doing this will probably make
your test code look more clean, keep the number of places where you need to
change something as small as possible, and lets you reuse data that you already
have described.

A hello world test with it looks like this::

    import nose
    from monk_tf import fixture

    def test_hello():
        ''' say hello
        '''
        # set up
        h = fixture.Fixture('target_device.cfg')
        expected_out = "hello"
        # execute
        out = h.devs[0].cmd('echo "hello"')
        # assert
        nose.tools.eq_(expected_out, out)
        # tear down
        h.tear_down()

When using this layer setting up a device only takes one line of code. The rest
of the information is in the ``target_device.cfg`` file. :term:`MONK` currently 
comes with one text format parser predefined, which is the
:py:class:`~monk_tf.fixture.XiniParser`. ``Xini`` is short for
:term:`extended INI`. You may, however, use any data format you want, if you
extend the :py:class:`~monk_tf.fixture.AParser` class accordingly.

An example ``Xini`` data file might look like this::

    [device1]
        type=Device
        [[serial1]]
            type=SerialConnection
            port=/dev/ttyUSB1
            user=example
            password=secret

As you can see it looks like an :term:`INI` file. There are sections,
consisting of a title enclosed in squared brackets (``[]``) and lists of
properties, consisting of key-value pairs separated by equality signs (``=``).
The unusual part is that the section *serial1* is surrounded by two pairs of
squared brackets (``[]``). This is the specialty of this format indicating that
*serial1* is a subsection of *device1* and therefore is a nested section. This
nesting can be done unlimited, by surrounding a section with more and more
pairs of squared brackets (``[]``) according to the level of nesting intended.
In this example *serial1* belongs to *device1* and the types indicate the
corresponding :term:`MONK` object to be created.

Classes
-------
"""

import os
import sys
import logging

import configobj as config

import conn
import dev

logger = logging.getLogger(__name__)

############
#
# Exceptions
#
############

class AFixtureException(Exception):
    """ Base class for exceptions of the fixture layer.

    If you want to make sure that you catch all exceptions that are related
    to this layer, you should catch *AFixtureExceptions*. This also means
    that if you extend this list of exceptions you should inherit from this
    exception and not from :py:exc:`~exceptions.Exception`.
    """
    pass

class CantHandleException(AFixtureException):
    """ if none of the devices is able to handle a cmd_any() call
    """
    pass

class AParseException(AFixtureException):
    """ Base class for exceptions concerning parsing errors.
    """
    pass

class NotXiniException(AParseException):
    """
    is raised when a :term:`fixture file` could not be parsed as
    :term:`extended INI`.
    """
    pass

class CantParseException(AFixtureException):
    """ is raised when a Fixture cannot parse a given file.
    """
    pass

class NoDeviceException(AFixtureException):
    """ is raised when a :py:clas:`~monk_tf.fixture.Fixture` requires a device but has none.
    """

######################################################
#
# Parsers - Read a text file and be used like a dict()
#
######################################################

class AParser(dict):
    """ Base class for all parsers.

    Do not instantiate this class! This basically just provides the :term:`API`
    that is needed by :py:class:`~monk_tf.fixture.Fixture` to interact with the
    data that is parsed. Each child class should make sure that it always
    provides its parsed data like a :py:class:`dict` would. If you require your
    own parser, you can extend this. :py:class:`~monk_tf.fixture.XiniParser`
    provides a very basic example.
    """
    pass

class XiniParser(config.ConfigObj, AParser):
    """ Reads config files in :term:`extended INI` format.
    """

    def _load(self, infile, configspec):
        """ Changes exception type raised.

        Overwrites method from :py:class:`~configobj.ConfigObj` to raise a
        :py:class:`~monk_tf.fixture.NotXiniException` instead of a
        :py:class:`~configobj.ConfigObjError`.
        """
        try:
            self.file_error = True
            super(XiniParser, self)._load(infile, configspec)
        except config.ConfigObjError as e:
            t, val, traceback = sys.exc_info()
            raise NotXiniException, e.message, traceback

##############################################################
#
# Fixture Classes - creates MONK objects based on dictionaries
#
##############################################################

class Fixture(object):
    """ Creates :term:`MONK` objects based on dictionary like objects.

    This is the class that provides the fundamental feature of this layer. It
    reads data files by trying to parse them via its list of known parsers and
    if it succeeds, it creates :term:`MONK` objects based on the configuration
    given by the data file. Most likely these objects are one or more
    :py:class:`~monk_tf.dev.Device` objects that have at least one
    :py:class:`~monk_tf.conn.AConnection` object each. If more than one
    :term:`fixture file` is read containing the same name on the highest level,
    then the latest data gets used. This does not work on lower levels of
    nesting, though. If you attempt to overwrite lower levels of nesting, what
    actually happens is that the highest layer gets overwritten and you lose
    the data that was stored in the older objects. This is simply how
    :py:meth:`set.update` works.

    One source of data (either a file name or a child class of
    :py:class:`~monk_tf.fixture.AParser`) can be given to an object of this
    class by its constructer, others can be added afterwards with the
    :py:meth:`~monk_tf.fixture.Fixture.read` method. An example looks like
    this::

        import monk_tf.fixture as mf

        fixture = mf.Fixture('/etc/monk_tf/default_devices.cfg')
                .read('~/.monk/default_devices.cfg')
                # can also be a parser object
                .read(XiniParser('~/testsuite12345/suite_devices.cfg'))

    """

    _DEFAULT_CLASSES = {
        "Device" : dev.Device,
        "HydraDevice" : dev.Hydra,
        "SerialConnection" : conn.SerialConn,
        "SshConnection" : conn.SshConn,
    }

    _DEFAULT_PARSERS = [
        XiniParser,
    ]

    _DEFAULT_DEBUG_SOURCE = "MONK_DEBUG_SOURCE"

    def __init__(self, source=None, name=None, parsers=None, classes=None,
            lookfordbgsrc=True):
        """

        :param source: The :term:`fixture file` or
                       :py:class:`~monk_tf.fixture.AParser` object to be read.

        :param name: The name of this object.

        :param parsers: An :python:term:`iterable` of
                        :py:class:`~monk_tf.fixture.AParser` classes to be used
                        for parsing a given
                        :py:attr:`~monk_tf.fixture.Fixture.source`.

        :param classes: A :py:class:`dict` of classes to class names. Used for
                        parsing the type attribute in
                        :term:`fixture files<fixture file>`.

        :param lookfordbgsrc: If True an environment variable is looked for to
                              read a local debug config. If False it won't be
                              looked for.
        """
        self.name = name or self.__class__.__name__
        self._logger = logging.getLogger("{}:{}".format(__name__, self.name))
        self.devs = []
        self.parsers = parsers or self._DEFAULT_PARSERS
        self.classes = classes or self._DEFAULT_CLASSES
        self.props = {}
        if source:
            self._update_props(
                    self._parse(source))
        if lookfordbgsrc and self._DEFAULT_DEBUG_SOURCE in os.environ:
            self._logger.debug("load debug source from {}".format(
                self._DEFAULT_DEBUG_SOURCE))
            self._update_props(
                    self._parse(os.environ[self._DEFAULT_DEBUG_SOURCE]))
        else:
            self._logger.debug("no debug source file found")
        self._initialize()


    def read(self, source):
        """ Read more data, either as a file name or as a parser.

        :param source: the data source; either a file name or a
                       :py:class:`~monk_tf.fixture.AParser` child class
                       instance.

        :return: self
        """
        self._logger.debug("read: " + str(source))
        props = self._parse(source)
        self._update_props(props)
        self._initialize()
        return self

    def _parse(self, source):
        """ Parse data file.

        :param source: the data source; either a file name or a
                       :py:class:`~monk_tf.fixture.AParser` child class
                       instance.

        :return: Returns a :py:class:`~monk_tf.fixture.AParser` instance.
        :raises: :py:class:`~monk_tf.fixture.CantParseException`
        """
        self._logger.debug("parse: " + str(source))
        if isinstance(source, AParser):
            return source
        else:
            for parser in self.parsers:
                try:
                    return parser(source)
                except AParseException as e:
                    self._logger.exception(e)
                    continue
            raise CantParseException()

    def _update_props(self, props):
        """ Updates the properties with a dictionary-like object.

        This basically uses :py:meth:`dict.update` to update
        :py:attr:`self.props <~monk_tf.fixture.Fixture.props>` with a new set
        of data.

        :param props: object that can be used with :py:meth:`dict.update`
        """
        self._logger.debug("add props: " + str(props))
        self.props.update(props)
        self._logger.debug("final props: " + str(props))

    def _initialize(self):
        """ Create :term:`MONK` objects based on self's properties.
        """
        self._logger.debug("initialize with props: " + str(self.props))
        self.devs = [self._parse_section(d, self.props[d]) for d in self.props.keys()]

    def _parse_section(self, name, section):
        self._logger.debug("parse_section({},{},{})".format(
            str(name),
            type(section).__name__,
            section.keys()
        ))
        sectype = self.classes[section.pop("type")]
        if "conns" in section:
            cs = section.pop("conns")
            section["conns"] = [self._parse_section(s, cs[s]) for s in cs]
        section["name"] = name
        return sectype(**section)

    def cmd_first(self, msg, expect=None, timeout=30, login_timeout=None):
        """ call :py:meth:`cmd` from first :py:class:`~monk_tf.device.Device`
        """
        self.log("cmd_first({},{},{},{})".format(
            msg, expect, timeout, login_timeout))
        try:
            return self.devs[0].cmd(msg)
        except IndexError:
            raise NoDeviceException("this fixture has no device loaded")

    def cmd_any(self, msg, expect=None, timeout=30, login_timeout=None):
        self.log("cmd_any({},{},{},{})".format(
            msg, expect, timeout, login_timeout))
        if not self.devs:
            self._logger.warning("fixture has no devices for sending commands to")
        for dev in self.devs:
            try:
                self.log("send cmd '{}' to device '{}'".format(
                    msg.encode("string-escape"),
                    dev,
                ))
                return dev.cmd(
                        msg=msg,
                        expect=expect,
                        timeout=timeout,
                        login_timeout=login_timeout,
                )
            except Exception as e:
                self._logger.exception(e)
            raise CantHandleException(
                    "fixt:'{}',devs:{},could not send cmd '{}'".format(
                        self.name,
                        map(str, self.devs),
                        msg.encode('string-escape'),
            ))

    def cmd_all(self, msg, expect=None, timeout=30, login_timeout=None):
        self.log("cmd_any({},{},{},{})".format(
            msg, expect, timeout, login_timeout))
        if not self.devs:
            self._logger.warning("fixture has no devices for sending commands to")
        for dev in self.devs:
            self.log("send cmd '{}' to device '{}'".format(
                msg.encode("string-escape"),
                dev,
            ))
            return dev.cmd(
                    msg=msg,
                    expect=expect,
                    timeout=timeout,
                    login_timeout=login_timeout,
            )

    def reset_config_all(self):
        if not self.devs:
            self._logger.warning("fixture has no devices for sending commands to")
        for dev in self.devs:
            dev.reset_config()


    def log(self, msg):
        self._logger.debug(msg)

    def tear_down(self):
        """ Can be used for explicit destruction of managed objects.

        This should be called in every :term:`test case` as the last step.

        """
        for device in self.devs:
            try:
                del device
            except Exception as e:
                logger.exception(e)
        self.devs = []

    def __str__(self):
        return "{cls}.devs:{devs}".format(
                cls=self.__class__.__name__,
                devs=[str(d) for d in self.devs],
        )
