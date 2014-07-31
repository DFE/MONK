#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MONK Automated Testing Framework
#
# Copyright (C) 2013 DResearch Fahrzeugelektronik GmbH
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 2 of the License, or (at your option) any later version.
#

import os
import sys

import monk_tf

try:
    from setuptools import setup
except ImportError as error:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    sys.argv = [sys.argv[0], 'sdist', 'upload']


def read(name):
    try:
        with open(name, 'r') as f:
            return f.read()
    except IOError:
        return ""

setup(
    name=monk_tf.__title__,
    version=monk_tf.__version__,
    description = "regression test scripting framework for embedded systems developers",
    long_description = read("README.rst") + "\n\n" + read("CHANGES.rst"),
    author = monk_tf.__author__,
    author_email = "project-monk@dresearch-fe.de",
    url="https://github.com/DFE/MONK",
    packages=[monk_tf.__title__],
    license=read("LICENSE.txt"),
    zip_safe=False,
    install_requires = [
        "pexpect >= 3.3",
        "requests >= 2.2.1",
        "configobj >=4.7.2",
    ],provides = [
        "{} ({})".format(monk_tf.__title__, monk_tf.__version__)
    ],
    test_suite = "nose.collector",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development",
        "Topic :: Software Development :: Testing",
        "Topic :: Terminals :: Serial",
    ],
)
