##
#    Copyright (C) 2015 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from django import test
from django.utils import unittest

from bitfield import BitHandler

from website.templatetags import inboxen_flags


class InboxFlagTestCase(test.TestCase):
    def test_no_error(self):
        flag_obj = BitHandler(6, ["new", "read", "somefakeflag", "someother"])

        inboxen_flags.render_flags(flag_obj)

    def test_invert(self):
        flag_obj = BitHandler(3, ["new", "read"])
        output = inboxen_flags.render_flags(flag_obj)

        self.assertNotIn("Unread message", output)
        self.assertNotIn("label-info", output)

    def test_multiple(self):
        flag_obj = BitHandler(1, ["new", "read"])
        output = inboxen_flags.render_flags(flag_obj)

        self.assertIn("Unread message", output)
        self.assertIn("label-info", output)
        self.assertIn("New messages", output)
        self.assertIn("label-primary", output)
        self.assertEqual(output.count("span"), 4)

    def test_empty(self):
        flag_obj = BitHandler(2, ["new", "read"])
        output = inboxen_flags.render_flags(flag_obj)

        self.assertEqual(output, "")
