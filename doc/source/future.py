#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MONK automated test framework board controller handling
#
# Copyright (C) 2013 DResearch Fahrzeugelektronik GmbH
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version
# 2 of the License, or (at your option) any later version.
#

"""
contains an example of how MONK should look like in v1.0
"""

import monk_tf as monk
import your_testframework as tf

class MonkTestcase(monk.TestCase):
    """an example TestCase """

    def test_simple(self):
        self.prepare(
            env = monk.SingleUsecase(), #default
            bins = (monk.Binary("https://github.com/DFE/example"),),
            logs = (
                monk.Log(
                    path = "/var/log/messages",
                    contains = ("regex1","regex2"),
                    line_handling = monk.Log.LAST,
                ),monk.Log("~/.example.log",("regex3",))
            ),
            cmds = (monk.CMD(
                cmd_line = "example --args",
                contains = ("regex4",)
            ),)
        ) # end of prepare
        tf.change_whatever_you_want()
        self.execute()
        self.assert_env()
        self.clean()
