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
your test code look more clean, keep the amount of places where you need to
change something as small as possible, and lets you reuse data that you already
have described.

A hello world test with it looks like this::

    import nose
    from monk_tf import harness

    def test_hello():
        ''' say hello
        '''
        # set up
        h = harness.Harness('target_device.cfg')
        expected_out = "hello"
        # execute
        out = h.devs[0].cmd('echo "hello"')
        # assert
        nose.tools.eq_(expected_out, out)
        # tear down
        h.tear_down()

So using this layer setting up a device only takes one line of code. The rest
of the information is in that ``target_device.cfg`` file. Although this data
file can have any format you want, MONK currently only comes with one text
format parser predefined, which is the :py:class:`~monk_tf.harness.XiniParser`.
The ``Xini`` is short for :term:`extended INI`. An example data file might look
like this::

    [device1]
        type=Device
        [[serial1]]
            type=SerialConnection
            port=/dev/ttyUSB1
            user=example
            password=secret

As you can see it looks like a :term:`INI` file. There are sections, consisting
of a title enclosed in squared brackets (``[]``) and lists of properties,
consisting of equal-sign (``=``) separated key-value pairs. The unusual part is
that the section *serial1* is surrounded by two pairs of squared brackets
(``[]``). This is the specialty of this format, because it means that *serial1*
is a subsection of *device1* and is therefore a nested section. This nesting
can be done unlimited, by surrounding a section with more and more pairs of
squared brackets (``[]``) according to the level of nesting that should be
achieved. Thus in this example *serial1* belongs to *device1* and the types
show which corresponding MONK object should be created.

Classes
-------
"""

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

class ADeviceException(Exception):
    """ Base class for Exceptions of the device layer.

    If you want to make sure that you catch all Exceptions that are related
    with this layer, then you should catch *ADeviceExceptions*. This also means
    that if you extend this list of exceptions you should inherit from this
    exception and not from :py:exc:`~exceptions.Exception`.
    """
    pass

class AParseException(ADeviceException):
    """ Base class for exceptions when a parsing error occurs.
    """
    pass

class NotXiniException(AParseException):
    """ Could not be parsed as :term:`extended INI`.
    """
    pass

class CantParseException(ADeviceException):
    """ Occurs, when a Harness can not parse a given file
    """
    pass

######################################################
#
# Parsers - Read a text file and be used like a dict()
#
######################################################

class AParser(dict):
    """ Base class for all Parsers.

    Do not instantiate this class! This basically just provides the :term:`API`
    that is needed by :py:class:`~monk_tf.harness.Harness` to interact with the
    data that is parsed. Each child class should make sure that it always
    provides its parsed data like a :py:class:`dict` would. If you require your
    own parser, you can extend this and look at
    :py:class:`~monk_tf.harness.XiniParser` for a very basic example.
    """
    pass

class XiniParser(config.ConfigObj, AParser):
    """ Reads config files in :term:`extended INI` format.
    """

    def _load(self, infile, configspec):
        """ changes exception type raised

        Overwrites method from :py:class:`~configobj.ConfigObj` to raise a
        :py:class:`~monk_tf.harness.NotXiniException` instead of a
        :py:class:`~configobj.ConfigObjError`.
        """
        try:
            super(XiniParser, self)._load(infile, configspec)
        except config.ConfigObjError as e:
            t, val, traceback = sys.exc_info()
            raise NotXiniException, e.message, traceback

##############################################################
#
# Harness Classes - creates MONK objects based on dictionaries
#
##############################################################

class Harness(object):
    """ Creates MONK objects based on dictionary like objects.

    This is the class that provides the fundamental feature of this layer. It
    reads data files by trying to parse them though its list of known parsers
    and if it succeeds, it creates MONK objects based on the configuration
    given by the data file. Most likely these objects are one or more devices
    that have at least one connection each. If more than one data file is read
    containing the same name on the highest level, then the latest data gets
    used. This does not work on lower levels of nesting, though.

    One source of data (either a filename or a child class of
    :py:class:`~monk_tf.harness.AParser`) can be given to an object of this
    class by its constructer, others can be added afterwards with the
    :py:meth:`~monk_tf.harness.Harness.read` method. An example looks like
    this::

        import monk_tf.harness as mh

        h = mh.Harness('/etc/monk_tf/default_devices.cfg')
                .read('~/.monk/default_devices.cfg')
                # can also be a parser object
                .read(XiniParser('~/testsuite12345/suite_devices.cfg'))

    """

    _DEFAULT_CLASSES = {
        "Device" : dev.Device,
        "SerialConnection" : conn.SerialConnection,
    }

    _DEFAULT_PARSERS = [
        XiniParser,
    ]

    def __init__(self, source=None, start_props=None, name=None, parsers=None,
            classes=None):
        self.name = name or self.__class__.__name__
        self._logger = logging.getLogger("{}:{}".format(__name__, self.name))
        self.devs = []
        self.parsers = parsers or self._DEFAULT_PARSERS
        self.classes = classes or self._DEFAULT_CLASSES
        self.props = {}
        if source:
            self.read(source)

    def read(self, source):
        """ Read more data, either as a filename or as a parser.

        :param source: the data source; either a filename or a
                       :py:class:`~monk_tf.harness.AParser` child class
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

        :param source: the data source; either a filename or a
                       :py:class:`~monk_tf.harness.AParser` child class
                       instance.

        :return: Returns a :py:class:`~monk_tf.harness.AParser` instance.
        :raises: :py:class:`~monk_tf.harness.CantParseException`
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
        :py:attr:`self.props <~monk_tf.harness.Harness.props>` with a new set
        of data.

        :param props: object that can be used with :py:meth:`dict.update`
        """
        self._logger.debug("add props: " + str(props))
        self.props.update(props)

    def _initialize(self):
        """ Create MONK objects based on self's properties.
        """
        self._logger.debug("initialize with props: " + str(self.props))
        self.devs = []
        for dname in self.props.keys():
            dconf = dict(self.props[dname])
            dclass = self.classes[dconf.pop("type")]
            dconns = []
            for cname in dconf.keys():
                cconf = dict(dconf[cname])
                cclass = self.classes[cconf.pop("type")]
                cconf['name'] = cname
                dconns.append(cclass(**cconf))
            self.devs.append(dclass(name=dname, conns=dconns))

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
