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

from distutils.core import setup

project = 'monk_tf'
src_path = 'src'

setup(
    name=project,
    version='v0.1',
    description = 'a test framework for embedded systems',
    author = 'DResearch Fahrzeugelektronik GmbH',
    author_email = 'project-monk@dresearch-fe.de',
    url='https://github.com/DFE/MONK',
    packages=[project],
    package_dir = { '' : src_path }
)
