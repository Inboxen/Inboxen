# -*- coding: utf-8 -*-
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

from bitfield import BitHandler

from inboxen.templatetags import inboxen_flags, inboxen_selector


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

    def test_disabled(self):
        flag_obj = BitHandler(5, ["new", "read", "disabled"])
        output = inboxen_flags.render_flags(flag_obj)

        self.assertIn("Inbox has been disabled", output)
        self.assertIn("label-default", output)
        self.assertEqual(output.count("span"), 2)

    def test_unicode(self):
        inboxen_flags.FLAGS_TO_TAGS["snowman"] = {
            "title": u"Snowman",
            "str": u"☃",
            "class": "awesome-snowman",
            "inverse": False
        }
        try:
            flag_obj = BitHandler(3, ["snowman"])
            inboxen_flags.render_flags(flag_obj)
        finally:
            del inboxen_flags.FLAGS_TO_TAGS["snowman"]


class SelectorEscapeTestCase(test.TestCase):
    def test_escapes(self):
        input_string = "me@inboxen.org"
        expected_string = r"me\\@inboxen\\.org"
        result = inboxen_selector.escape_selector(input_string)

        self.assertEqual(expected_string, result)

    def test_escapes_in_data(self):
        input_string = "me@inboxen.org"
        expected_string = r"me\@inboxen\.org"
        result = inboxen_selector.escape_selector(input_string, as_data=True)

        self.assertEqual(expected_string, result)
