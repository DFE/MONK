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
:py:class:`~monk_tf.conn.ConnectionBase` objects by yourself, you can also
choose to put corresponding data in a separate file and let this layer handle
the object concstruction and destruction for you. Doing this will probably make
your test code look more clean, keep the number of places where you need to
change something as small as possible, and enables you to reuse data that you
already have described.

A hello world test with a fixture looks like this:

.. code-block:: python

    import nose
    from monk_tf import fixture

    def test_hello():
        ''' say hello
        '''
        with fixture.Fixture(__file__) as (fix, dev):
            # set up
            expected_out = "hello"
            # execute
            retcode, out = dev.cmd('echo "hello"')
            # assert
            nose.tools.eq_(expected_out, out)
            # tear down - automatically done by Fixture

Everything is handled in a context that manages the fixture and your
:term:`target device`. The Fixture is automatically looking for ``fixture.cfg``
in the current directory or its parents. The ``fixture.cfg`` contains the data
that is necessary to build your test fixture. This includes connection data
like IP, user name, and password. MONK separates this data from the code, that
the tests can be executed on different :term:`target devices<target device>`
without changing the tests themselves. The format of these files is quite close
to ini files, just with an added layer of depth, enabling sections to contain
other sections if the inner section is surrounded by an additional set of
square brackets (``[]``).

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
from os import environ
import os.path as op
import sys
import logging
import collections
import time
import inspect
import io
import traceback
import datetime

import configobj as config

import monk_tf.general_purpose as gp
import monk_tf.conn as mc
import monk_tf.dev as md

logger = logging.getLogger(__name__)

############
#
# Exceptions
#
############

class AFixtureException(gp.MonkException):
    """ Base class for exceptions of the fixture layer.

    If you want to make sure that you catch all exceptions that are related
    to this layer, you should catch *AFixtureExceptions*. This also means
    that if you extend this list of exceptions you should inherit from this
    exception and not from :py:exc:`~exceptions.Exception`.
    """
    pass

class NoDevsChosenException(AFixtureException):
    """ If the use_devs attribute is not set this is raised
    """
    pass

class NoSectypeException(AFixtureException):
    """ If no name can be derived from parsing a section
    """
    pass

class NoDevicesDefinedException(AFixtureException):
    """ is raised when we found out that there are no devices.

    Currently it makes no sense to use a fixture without devices.
    """
    pass

class AParseException(AFixtureException):
    """ Base class for exceptions concerning parsing errors.
    """
    pass

class CantParseException(AFixtureException):
    """ is raised when a Fixture cannot parse a given file.
    """
    pass

class NoPropsException(AFixtureException):
    """ is raised when
    """
    pass

class NoDeviceException(AFixtureException):
    """ is raised when a :py:clas:`~monk_tf.fixture.Fixture` requires a device but has none.
    """
    pass

class WrongNameException(AFixtureException):
    """ is raised when no devs with a given name could be found.
    """
    pass

class UnknownTypeException(AFixtureException):
    """ Handler Type was not recognized
    """
    pass


##############################################################
#
# Fixture Classes - creates MONK objects based on dictionaries
#
##############################################################

class LogManager(gp.MonkObject):
    """ managing configuration and setup of logging mechanics

    Might strongly interact with your nose config or similar.
    """

    def __init__(self, **config):
        super(LogManager, self).__init__(
                name=config.pop("name",None),
                module=__name__,
        )
        self.log("load LogManager with config:" + str(config))

    def testlog(self, msg):
        self.testlog.warning(msg)

class LogHandler(gp.MonkObject):

    _LOGLEVELS = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }

    def __init__(self, name, sink, target, format, level):
        super(LogHandler, self).__init__(
                name=name,
                module=__name__,
        )
        self.sink = sink
        self.target = self.config_subs(target)
        self.format = format
        self.level = level

    def register(self):
        self.pre_register()
        self.log("loglevel:{}".format(self.level))
        self.handler.setLevel(self._LOGLEVELS[self.level])
        self.log("format:{}".format(self.format))
        self.handler.setFormatter(logging.Formatter(
            fmt=self.format,
        ))
        self.log("register at logger '{}'".format(
            self.target,
        ))
        logging.getLogger(self.target).addHandler(self.handler)
        logging.getLogger(self.target).setLevel(self._LOGLEVELS[self.level])
        self.post_register()

    def config_subs(self, txt, subs=None):
        """ replace the strings in the config that we have reasonable values for
        """
        substitutes = subs or {
                "testcase" : find_testname(),
                "rootlogger" : "",
                "suitename" : environ.get("SUITE", "suite"),
                "datetime" : datetime.datetime.now().strftime("%y%m%d-%H%M%S"),
        }
        return txt % substitutes

    def pre_register(self):
        pass

    def post_register(self):
        pass


class StreamHandler(LogHandler):
    def pre_register(self):
        # workaround for strange nose handlers
        for h in logging.getLogger(self.target).handlers:
            if isinstance(h, logging.StreamHandler):
                logging.getLogger(self.target).removeHandler(h)
        stream = sys.stdout if self.sink == "stdout" else sys.stderr
        self.log("stream:" + str(sys.stdout))
        self.handler = logging.StreamHandler(stream)

class FileHandler(LogHandler):
    def pre_register(self):
        self.handler = logging.FileHandler(self.config_subs(self.sink))



class Fixture(gp.MonkObject):
    """ Creates :term:`MONK` objects based on dictionary like objects.

    Use this class if you want to seperate the details of your MONK objects
    from your code. Also use it if you want to write tests with it, as
    described above.
    """


    def __init__(self, call_location, name=None,
            fixture_locations=None, parsers=None):
        """
        :param call_location: the __file__ from where this is called.

        :param parsers: a dictionary of name:parser_function pairs that can
                        interpret a fixture file section and generate an object
                        based on that.

        :param fixture_locations: where to look for fixture files
        """
        super(Fixture, self).__init__(
            name=name,
            module=__name__,
        )
        self.call_location = call_location
        self.call_path = op.dirname(op.abspath(self.call_location))
        self.devs = {}
        self.ignore_exceptions = []
        self.props = config.ConfigObj()
        self.fixture_locations = fixture_locations or self.default_fixturelocations()
        self.read(loc for loc in self.fixture_locations if op.isfile(loc))

    @property
    def firstdev(self):
        return self.devs.get(self.use_devs[0])

    @property
    def parsers(self):
        try:
            return self._parsers
        except AttributeError:
            # trigger default setting
            self.parsers = None
            return self._parsers


    def default_parsers(self):
        return {
            "Device" : self.parse_device,
            "conns" : self.parse_conns,
            "SshConnection" : self.parse_sshconn,
            "SerialConnection" : self.parse_serialconn,
            "logging" : self.parse_logging,
            "StreamHandler" : self.parse_streamhandler,
            "FileHandler" : self.parse_filehandler,
        }

    @parsers.setter
    def parsers(self, parsers):
        self._parsers = parsers or self.default_parsers()

    def default_fixturelocations(self):
        """ this is preferred over a list/dict

        because some paths need to be set dynamically!
        """
        locs = [
            self.call_path + "/../fixture.cfg",
        ]
        self.log("read default fixturelocations: {}".format(self, locs))
        return locs

    def read(self, sources):
        """ Read more data, either as a file name or as a parser.

        :param sources: a iterable of data sources; each is either a file name
                        or a :py:class:`~monk_tf.fixture.AParser` child class
                        instance.

        :return: self
        """
        self.log("read: " + str(sources))
        self.log("deactivate everything before updating data")
        self.tear_down()
        for source in sources:
            self.log("merge source: '{}'".format(source))
            self.props.merge(config.ConfigObj(source, interpolation=False))
        self._initialize()
        return self

    def _initialize(self):
        """ Create :term:`MONK` objects based on self's properties.
        """
        self._logger.debug("initialize with props: " + str(self.props))
        if not self.props:
            raise NoPropsException("have you created and added any fixture files?")
        parsed = {}
        for name, value in self.props.items():
            parsed[name] = self._parse_section(name, value)
        self.update(**parsed)

    def update(self, **kwargs):
        """ update the externally manageable data of this fixture object
        """
        self.testlogger = kwargs.pop("logging", self._logger)
        self.use_devs = [devname.strip() for devname in kwargs.pop("use_devs", []) if devname]
        if not self.use_devs:
            raise NoDevsChosenException("You need to set a use_devs property to your config file which contains a list of comma separated device names that are defined in your [[conns]] block")
        self.devs = {n:d for n,d in kwargs.items()}

    def _find_sectype(self, name, section):
        """ try to retrieve the section type, preferably by name

        :param name: the name of the section and a possible source of the type

        :param section: a dictionary, containing all the attributes necessary
                        to create an object of the sectype. If it contains a
                        "type" property this can be used to identify the type.

        :return: the section type, as expected as key for fixture.parsers
        """
        try:
            return name if name in self.parsers else section.pop("type")
        except KeyError:
            raise NoSectypeException("for section {}:\n{}".format(name, section))

    def _parse_section(self, name, section):
        """ parse a deep dictionary depth first, generate objects bottom up

        :name: the name of the current section
        :section: the dictionary containing

        :return: the object that is generated by this section
        """
        try:
            self._logger.debug("parse_section({},{},{})".format(
                str(name),
                type(section).__name__,
                list(section.keys()),
            ))
        except AttributeError as e:
            # duck tested that this is not a dcitionary.
            # Non dictionaries are normal types like str or int.
            # So they are just returned, because they don't need parsing.
            return section
        # sectype often means the resulting object type, e.g. SshConn
        sectype=self._find_sectype(name, section)
        # first parse section's properties, then apply them
        self.log("traverse subsections iteratively")
        section = {k:self._parse_section(k,v) for k,v in section.items()}
        self.log("create object for section")
        return self.parsers[sectype](name, sectype, section)

    def parse_serialconn(self, name, sectype, section):
        section["name"] = name
        return mc.SerialConn(**section)

    def parse_sshconn(self, name, sectype, section):
        section["name"] = name
        return mc.SshConn(**section)

    def parse_device(self, name, sectype, section):
        section["name"] = name
        return md.Device(**section)

    def parse_conns(self, name, sectype, section):
        return {k:v for k,v in section.items()}

    def parse_logging(self, name, sectype, section):
        for handler in section.values():
            handler.register()
        self.testlogger = logging.getLogger(find_testname())
        return self.testlogger

    def parse_streamhandler(self, name, sectype, section):
        section["name"] = name
        return StreamHandler(**section)

    def parse_filehandler(self, name, sectype, section):
        section["name"] = name
        return FileHandler(**section)

    def testlog(self, msg):
        self.testlogger.warning(msg)

    def tear_down(self):
        """ Can be used for explicit destruction of managed objects.

        This should be called in every :term:`test case` as the last step.

        """
        self.log("teardown")
        for name, device in self.devs.items():
            device.close_all()

    def __str__(self):
        if hasattr(self, "devs") and self.devs:
            return str(self.devs)
        else:
            return repr(self)

    def __enter__(self):
        self.log("__enter__ ")
        return [self, self.firstdev, self.testlogger]

    def __exit__(self, exception_type, exception_val, tb):
        self.log("__exit__ ")
        if exception_type and exception_type not in self.ignore_exceptions:
            buff = io.StringIO()
            traceback.print_tb(tb, file=buff)
            self.testlogger.warning("\n{}:{}:\n{}".format(exception_type.__name__, exception_val, buff.getvalue()))
        self.tear_down()

_LOGFINDERS = ["test_", "setup"]

# note that this is a function not a method
def find_testname(grab_txts=None):
    grab_txts = grab_txts or _LOGFINDERS
    for txt in grab_txts:
        for caller in inspect.stack():
            name = caller[3]
            if name.startswith(txt):
                return name
    return grab_txts[0]
