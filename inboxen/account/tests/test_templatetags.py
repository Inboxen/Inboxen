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

from unittest import mock

from django.template import Context, Template

from inboxen.account.templatetags import inboxen_account
from inboxen.test import InboxenTestCase


class AccountMenuTestCase(InboxenTestCase):

    def test_handles_utf8(self):
        test_dict = (("user-settings", u"☃"),)
        with mock.patch.object(inboxen_account.AccountMenuNode, "menu", test_dict):
            template = Template("{% load inboxen_account %}{% account_menu 'user-settings' %}")
            template.render(Context({}))
