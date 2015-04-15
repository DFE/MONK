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

import monk_tf.conn as conn
import monk_tf.dev as dev

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

class LogManager(object):
    """ managing configuration and setup of logging mechanics

    Might strongly interact with your nose config or similar.
    """

    _LOGLEVELS = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }

    # this list is hierarchical, if the first prefix succeeds the others aren't
    # tried
    _LOGFINDERS = ["test_", "setup"]

    def __init__(self, config):
        self.log("load LogManager with config:" + str(config))
        for hname, handler in config.items():
            self.log("create:{}:{}".format(hname, handler))
            # replace possible target strings, like the name of the testcase
            target = self.config_subs(handler["target"])
            hobj=None
            if handler["type"] == "StreamHandler":
                # workaround for strange nose handlers
                for h in logging.getLogger(target).handlers:
                    if isinstance(h, logging.StreamHandler):
                        logging.getLogger(target).removeHandler(h)
                stream = sys.stdout if handler["sink"] == "stdout" else sys.stderr
                self.log("stream:" + str(sys.stdout))
                hobj = logging.StreamHandler(stream)
            elif handler["type"] == "FileHandler":
                self.log("file:" + str(handler["sink"]))
                hobj = logging.FileHandler(self.config_subs(handler["sink"]))
            else:
                raise UnknownTypeException("handler of type {} unfamiliar, spelling error?".format(handler["type"]))
            self.log("loglevel:{}".format(self._LOGLEVELS[handler["level"]]))
            hobj.setLevel(self._LOGLEVELS[handler["level"]])
            self.log("format:{}".format(handler["format"]))
            hobj.setFormatter(logging.Formatter(
                fmt=handler["format"],
            ))
            self.log("add handler '{}' (obj:{}) to logger '{}' (unformatted target '{}')".format(
                hname,
                hobj,
                target,
                handler["target"],
            ))
            logging.getLogger(target).addHandler(hobj)
            logging.getLogger(target).setLevel(
                    self._LOGLEVELS[handler["level"]])
        self.log("done with all log handlers")

    def config_subs(self, txt, subs=None):
        """ replace the strings in the config that we have reasonable values for
        """
        substitutes = subs or {
                "testcase" : self.find_testname(),
                "rootlogger" : "",
                "suitename" : environ.get("SUITE", "suite"),
                "datetime" : datetime.datetime.now().strftime("%y%m%d-%H%M%S"),
        }
        return txt % substitutes

    def log(self, msg):
        logging.getLogger(self.__class__.__name__).debug(msg)

    def testlog(self, msg):
        self.testlog.warning(msg)

    @property
    def testlogger(self):
        try:
            return self._testlogger
        except:
            self._testlogger = logging.getLogger(self.find_testname())
            return self._testlogger

    def find_testname(self, grab_txts=None):
        grab_txts = grab_txts or self._LOGFINDERS
        for txt in grab_txts:
            for caller in inspect.stack():
                name = caller[3]
                if name.startswith(txt):
                    return name
        self.log("haven't found a test name, but I also don't want the root logger")
        return grab_txts[0]

class Fixture(object):
    """ Creates :term:`MONK` objects based on dictionary like objects.

    Use this class if you want to seperate the details of your MONK objects
    from your code. Also use it if you want to write tests with it, as
    described above.
    """

    _DEFAULT_CLASSES = {
        "Device" : dev.Device,
        "SerialConnection" : conn.SerialConn,
        "SshConnection" : conn.SshConn,
        "logging" : LogManager,
    }

    _DEFAULT_DEBUG_SOURCE = "MONK_DEBUG_SOURCE"

    def __init__(self, call_location, name=None, classes=None,
            fixture_locations=None):
        """

        :param call_location: the __file__ from where this is called.

        :param classes: A :py:class:`dict` of classes to class names. Used for
                        parsing the type attribute in
                        :term:`fixture files<fixture file>`.


        :param fixture_locations: where to look for fixture files
        """
        self.call_location = call_location
        self.call_path = op.dirname(op.abspath(self.call_location))
        self._logger = logging.getLogger("{}:{}".format(
            __name__,
            name or self.__class__.__name__,
        ))
        self.devs = []
        self._devs_dict = {}
        self.ignore_exceptions = []
        self.classes = classes or self._DEFAULT_CLASSES
        self.props = config.ConfigObj()
        self.fixture_locations = fixture_locations or self.default_fixturelocations()
        self.read(loc for loc in self.fixture_locations if op.isfile(loc))

    def default_fixturelocations(self):
        # this is preferred over a list/dict, because some paths need to be set
        # dynamically!
        locs = [
                self.call_path + "/../fixture.cfg",
        ]
        self.log("read default fixturelocations: {}".format(self, locs))
        return locs

    @property
    def name(self):
        """ the fixture object's and the logger's name
        """
        return self._logger.name

    @name.setter
    def name(self, new_name):
        self._logger = logging.getLogger(new_name)

    def _parent_dirs(self, path):
        """ generate parent directories for path
        """
        while True:
            yield path
            mem = op.dirname(path)
            if path == mem:
                break
            else:
                path = mem


    def read(self, sources):
        """ Read more data, either as a file name or as a parser.

        :param sources: a iterable of data sources; each is either a file name
                        or a :py:class:`~monk_tf.fixture.AParser` child class
                        instance.

        :return: self
        """
        self.log("read: " + str(sources))
        self.log("make sure that you are teared down completely before getting started")
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
        if self.props:
            self.devs = [self._parse_section(d, self.props[d]) for d in self.props]
            # TODO workaround because logging stuff produces None element(s)
            self.devs = [d for d in self.devs if d]
        else:
            raise NoPropsException("have you created any fixture files?")

    def _parse_section(self, name, section):
        self._logger.debug("parse_section({},{},{})".format(
            str(name),
            type(section).__name__,
            list(section.keys()),
        ))
        # TODO special cases suck, improve!
        if name == "logging":
            self.logmanager = self.classes["logging"](section)
            return
        # TODO section parsing should be wrapped in handlers
        #      so that they can be extended without overwrites
        try:
            sectype = self.classes[section.pop("type")]
        except KeyError as e:
            self.log("section has no type, trying the name")
            try:
                sectype = self.classes[name]
            except KeyError as e:
                self.log("section {} has no type, therefore it is assumed to only contain data, no further parsing will be applied".format(name))
                return section
        if "conns" in section:
            cs = section.pop("conns")
            section["conns"] = [self._parse_section(s, cs[s]) for s in cs]
        if "bcc" in section:
            self.log("DEPRECATED: Use bctrl instead of bcc")
            bs = section.pop("bcc")
            section["bctrl"] = self._parse_section("bctrl", bs)
        if "bctrl" in section:
            bs = section.pop("bctrl")
            section["bctrl"] = self._parse_section("bctrl", bs)
        if "api" in section:
            bs = section.pop("api")
            section["api"] = self._parse_section("api", bs)
        if "auth" in section:
            bs = section.pop("auth")
            section["auth"] = self._parse_section("auth", bs)
        section["name"] = name
        self.log("load section:" + str(sectype) + "," + str(section))
        return sectype(**section)

    @property
    def testlogger(self):
        if hasattr(self, "logmanager"):
            return self.logmanager.testlogger
        else:
            self.log("couldn't find logmanager, use my own")
            return self._logger

    def get_dev(self, which):
        """ if there are many devices, retreive one by name
        """
        try:
            return self.devs[which]
        except TypeError:
            try:
                return self._devs_dict[which]
            except KeyError:
                names = []
                for dev in self.devs:
                    if dev.name == which:
                        self._devs_dict[which] = dev
                        return dev
                    else:
                        names.append(dev.name)
                raise WrongNameException("Couldn't retreive connection with name '{}'. Available names are: {}".format(which, names))

    def log(self, msg):
        """ helper for the fixture object's logger to send debug messages
        """
        self._logger.debug(msg)

    def testlog(self, msg):
        self.testlogger.warning(msg)

    def tear_down(self):
        """ Can be used for explicit destruction of managed objects.

        This should be called in every :term:`test case` as the last step.

        """
        self.log("teardown")
        for device in self.devs:
            device.close_all()
        self.devs = []

    def __str__(self):
        return "{cls}.devs:{devs}".format(
                cls=self.__class__.__name__,
                devs=[str(d) for d in self.devs],
        )

    def __enter__(self):
        self.log("__enter__ ")
        return [self] + list(self.devs) + [self.testlogger]


    def __exit__(self, exception_type, exception_val, tb):
        self.log("__exit__ ")
        if exception_type and exception_type not in self.ignore_exceptions:
            buff = io.StringIO()
            traceback.print_tb(tb, file=buff)
            self.testlogger.warning("\n{}:{}:\n{}".format(exception_type.__name__, exception_val, buff.getvalue()))
        self.tear_down()
