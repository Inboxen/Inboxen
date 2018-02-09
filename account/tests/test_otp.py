##
#    Copyright (C) 2016 Jessica Tallon & Matt Molyneaux
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

import itertools

from django import test
from django.core import urlresolvers

from account.forms import SettingsForm, UsernameChangeForm, DeleteAccountForm
from inboxen.test import InboxenTestCase, MockRequest
from inboxen.tests import factories


class OtpTestCase(InboxenTestCase):
    def setUp(self):
        super(OtpTestCase, self).setUp()
        self.user = factories.UserFactory()
        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def test_sudo_required(self):
        urls = [
            urlresolvers.reverse("user-twofactor-setup"),
            urlresolvers.reverse("user-twofactor-backup"),
            urlresolvers.reverse("user-twofactor-disable"),
            urlresolvers.reverse("user-twofactor-qrcode"),
        ]
