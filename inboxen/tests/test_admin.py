##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core import urlresolvers


class AdminTestCase(test.TestCase):
    def setUp(self):
        self.factory = test.RequestFactory()

    def test_login_redirects(self):
        request = self.factory.get("/", {REDIRECT_FIELD_NAME: "/hello"})
        response = admin.site.login(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "%s?%s" % (urlresolvers.reverse("user-login"), "next=%2Fhello"))
