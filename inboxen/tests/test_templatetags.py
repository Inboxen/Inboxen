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

from bitfield import BitHandler
from django.template import Template
from django.template.backends.django import Template as DjangoTemplate
from django.utils import translation
import mock

from inboxen.templatetags import inboxen_admin_tags, inboxen_flags, inboxen_selector
from inboxen.test import InboxenTestCase
from inboxen.utils import flags as flag_utils


class InboxFlagTestCase(InboxenTestCase):
    def tearDown(self):
        translation.deactivate_all()

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

        self.assertEqual(output.strip(), "&nbsp;")

    def test_disabled(self):
        flag_obj = BitHandler(5, ["new", "read", "disabled"])
        output = inboxen_flags.render_flags(flag_obj)

        self.assertIn("Inbox has been disabled", output)
        self.assertIn("label-default", output)
        self.assertEqual(output.count("span"), 2)

    def test_lazy_gettext(self):
        flag_obj = BitHandler(1, ["new"])
        output = inboxen_flags.render_flags(flag_obj)
        self.assertIn(">New<", output)

        translation.activate("sv")
        output = inboxen_flags.render_flags(flag_obj)
        self.assertIn(">Ny<", output)

        # test a non-existing language
        translation.activate("bluhbluhbluh")
        output = inboxen_flags.render_flags(flag_obj)
        self.assertIn(">New<", output)


class InboxenAdminTestCase(InboxenTestCase):
    def test_domain(self):
        output = inboxen_admin_tags.render_domain(True)
        self.assertIn('<span class="label label-primary"', output)
        self.assertIn("Enabled", output)
        self.assertNotIn("Disabled", output)

        output = inboxen_admin_tags.render_domain(False)
        self.assertIn('<span class="label label-default"', output)
        self.assertIn("Disabled", output)
        self.assertNotIn("Enabled", output)

    def test_request(self):
        output = inboxen_admin_tags.render_request(True)
        self.assertIn('<span class="label label-primary"', output)
        self.assertIn("Grant", output)
        self.assertNotIn("Rejected", output)
        self.assertNotIn("Pending", output)

        output = inboxen_admin_tags.render_request(False)
        self.assertIn('<span class="label label-default"', output)
        self.assertNotIn("Grant", output)
        self.assertIn("Rejected", output)
        self.assertNotIn("Pending", output)

        output = inboxen_admin_tags.render_request(None)
        self.assertIn('<span class="label label-danger"', output)
        self.assertNotIn("Grant", output)
        self.assertNotIn("Rejected", output)
        self.assertIn("Pending", output)


class TemplateTagFactoryTestCase(InboxenTestCase):
    def test_create_render_bool_template_tag_invalid_value(self):
        func = flag_utils.create_render_bool_template_tag({})
        self.assertEqual(func("some value"), "&nbsp;")

    @mock.patch("inboxen.utils.flags.loader")
    def test_create_render_bool_template_tag_loads_template(self, mock_loader):
        mock_loader.get_template.return_value = DjangoTemplate(Template("Hello: {{ str }}"), mock_loader)

        func = flag_utils.create_render_bool_template_tag({1: {"str": "person"}, 2: {"str": "animal"}}, "test.html")
        self.assertEqual(func(1), "Hello: person")
        self.assertEqual(func(2), "Hello: animal")

        # check that loader was called with our "custom" template
        self.assertEqual(mock_loader.get_template.call_count, 1)
        self.assertEqual(mock_loader.get_template.call_args, [('test.html',), {}])

        # check default template name
        func = flag_utils.create_render_bool_template_tag({1: {"str": "person"}, 2: {"str": "animal"}})
        self.assertEqual(mock_loader.get_template.call_count, 2)
        self.assertEqual(mock_loader.get_template.call_args, [('inboxen/flags/bool.html',), {}])

    def test_create_render_bitfield_template_tag_no_values(self):
        # empty flag definition, so all values will be "invalid"
        func = flag_utils.create_render_bitfield_template_tag({})
        flag_obj = BitHandler(1 | 2, ["new", "read"])
        self.assertEqual(func(flag_obj).strip(), "&nbsp;")

    @mock.patch("inboxen.utils.flags.loader")
    def test_create_render_bitfield_template_tag_loads_template(self, mock_loader):
        template = Template("{% for obj in flags %}Hello: {{ obj.str }}\n{% endfor %}")
        mock_loader.get_template.return_value = DjangoTemplate(template, mock_loader)

        func = flag_utils.create_render_bitfield_template_tag(
                {"p": {"str": "person"}, "a": {"str": "animal"}}, "test.html")
        flag_obj = BitHandler(1 | 2, ["a", "p"])
        self.assertEqual(func(flag_obj), "Hello: animal\nHello: person\n")

    @mock.patch("inboxen.utils.flags.loader")
    def test_create_render_bitfield_template_tag_inverse(self, mock_loader):
        template = Template("{% for obj in flags %}Hello: {{ obj.str }}\n{% endfor %}")
        mock_loader.get_template.return_value = DjangoTemplate(template, mock_loader)

        func = flag_utils.create_render_bitfield_template_tag(
                {"p": {"str": "person", "inverse": True}, "a": {"str": "animal"}}, "test.html")
        flag_obj = BitHandler(1 | 2, ["a", "p"])
        self.assertEqual(func(flag_obj), "Hello: animal\n")
        flag_obj = BitHandler(1, ["a", "p"])
        self.assertEqual(func(flag_obj), "Hello: animal\nHello: person\n")

    @mock.patch("inboxen.utils.flags.loader")
    def test_create_render_bitfield_template_tag_singleton(self, mock_loader):
        template = Template("{% for obj in flags %}Hello: {{ obj.str }}\n{% endfor %}")
        mock_loader.get_template.return_value = DjangoTemplate(template, mock_loader)

        func = flag_utils.create_render_bitfield_template_tag(
                {"p": {"str": "person", "singleton": True}, "a": {"str": "animal"}}, "test.html")
        flag_obj = BitHandler(1 | 2, ["a", "p"])
        self.assertEqual(func(flag_obj), "Hello: person\n")

    def test_unicode(self):
        flags = {"snowman": {
            "title": u"Snowman",
            "str": u"☃",
            "class": "awesome-snowman",
        }}
        func = flag_utils.create_render_bitfield_template_tag(flags)
        flag_obj = BitHandler(1, ["snowman"])
        output = func(flag_obj)

        self.assertIn(u'<span class="label awesome-snowman"', output)
        self.assertIn(u"☃", output)


class SelectorEscapeTestCase(InboxenTestCase):
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
