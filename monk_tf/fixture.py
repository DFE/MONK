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
import os.path as op
import sys
import logging
import collections

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

##############################################################
#
# Fixture Classes - creates MONK objects based on dictionaries
#
##############################################################

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
    }

    _DEFAULT_DEBUG_SOURCE = "MONK_DEBUG_SOURCE"

    def __init__(self, call_location, name=None, classes=None,
            lookfordbgsrc=True, filename="fixture.cfg", auto_search=True):
        """

        :param call_location: the __file__ from where this is called.

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

        :param filename: the name of the file which contains the configuration.

        :param auto_search: if true, it will automatically search and load
                            fixture files.
        """
        self.call_location = op.dirname(op.abspath(call_location))
        self._logger = logging.getLogger("{}:{}".format(
            __name__,
            name or self.__class__.__name__,
        ))
        self.devs = []
        self._devs_dict = {}
        self.classes = classes or self._DEFAULT_CLASSES
        self.props = config.ConfigObj()
        self.filename = filename
        self.auto_search = auto_search
        # look if the user has a default config in his home dir
        if auto_search:
            self.log("autosearching for fixture files...")
            home_fixture = op.expanduser(op.join("~", self.filename))
            if op.exists(home_fixture):
                self.read(home_fixture)
            # starting from root load all fixtures from parent directories
            self.log("location:{}".format(self.call_location))
            self.log("parent_dirs:" + str(list(self._parent_dirs(self.call_location))))
            for p in reversed(list(self._parent_dirs(self.call_location))):
                fixture_file = op.join(p, self.filename)
                if op.exists(fixture_file):
                    self.read(fixture_file)
        else:
            self.log("auto search deactivated, loaded without looking for fixture files")

    @property
    def name(self):
        """ the fixture object's and the logger's name
        """
        return self._logger.name

    @name.setter
    def name(self, new_name):
        self._logger.name = new_name

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


    def read(self, source):
        """ Read more data, either as a file name or as a parser.

        :param source: the data source; either a file name or a
                       :py:class:`~monk_tf.fixture.AParser` child class
                       instance.

        :return: self
        """
        self._logger.debug("read: " + str(source))
        self.tear_down()
        self.props.merge(config.ConfigObj(source))
        self._initialize()
        return self

    def _initialize(self):
        """ Create :term:`MONK` objects based on self's properties.
        """
        self._logger.debug("initialize with props: " + str(self.props))
        if self.props:
            self.devs = [self._parse_section(d, self.props[d]) for d in self.props.viewkeys()]
        else:
            raise NoPropsException("have you created any fixture files?")

    def _parse_section(self, name, section):
        self._logger.debug("parse_section({},{},{})".format(
            str(name),
            type(section).__name__,
            list(section.keys())
        ))
        # TODO section parsing should be wrapped in handlers
        #      so that they can be extended without overwrites
        sectype = self.classes[section.pop("type")]
        if "conns" in section:
            cs = section.pop("conns")
            section["conns"] = [self._parse_section(s, cs[s]) for s in cs]
        if "bcc" in section:
            self.log("DEPRECATED: Use bctrl instead of bcc")
            bs = section.pop("bcc")
            section["bcc"] = self._parse_section("bcc", bs)
        if "bctrl" in section:
            bs = section.pop("bctrl")
            section["bcc"] = self._parse_section("bctrl", bs)
        section["name"] = name
        self.log("load section:" + str(sectype) + "," + str(section))
        return sectype(**section)

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
        self.log("__enter__")
        return [self] + list(self.devs)

    def __exit__(self, exception_type, exception_val, trace):
        self.log("__exit__")
        self.tear_down()
