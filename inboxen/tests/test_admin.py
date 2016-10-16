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
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core import urlresolvers, exceptions

from csp.middleware import CSPMiddleware

from inboxen import admin
from inboxen.tests import factories


class AdminTestCase(test.TestCase):
    def setUp(self):
        self.factory = test.RequestFactory()

    def test_login_redirects(self):
        request = self.factory.get("/", {REDIRECT_FIELD_NAME: "/hello"})
        response = admin.site.login(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "%s?%s" % (urlresolvers.reverse("user-login"), "next=%2Fhello"))

    def test_logout_redirects(self):
        request = self.factory.get("/")
        response = admin.site.logout(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "%s" % urlresolvers.reverse("user-logout"))

    def test_password_change_redirects(self):
        request = self.factory.get("/")
        response = admin.site.password_change(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "%s" % urlresolvers.reverse("user-password"))

        response = admin.site.password_change_done(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "%s" % urlresolvers.reverse("admin:index", current_app=admin.site.name))

    def test_has_permission(self):
        request = self.factory.get("/")
        request.user = factories.UserFactory()
        request.user.is_verified = lambda: True
        request.user.is_staff = True

        response = admin.site.admin_view(admin.site.index)(request)
        self.assertEqual(response.status_code, 200)

        request.user.is_verified = lambda: False
        request.user.is_staff = True
        with self.assertRaises(exceptions.PermissionDenied):
            admin.site.admin_view(admin.site.index)(request)

        request.user.is_verified = lambda: True
        request.user.is_staff = False
        response = admin.site.admin_view(admin.site.index)(request)
        self.assertEqual(response.status_code, 302)

    def test_csp_replace(self):
        request = self.factory.get("/")
        request.user = factories.UserFactory()
        request.user.is_verified = lambda: True
        request.user.is_staff = True
        middleware = CSPMiddleware()

        response = admin.site.admin_view(admin.site.index)(request)
        response = middleware.process_response(request, response)
        self.assertIn("script-src 'self' 'unsafe-inline'", response["content-security-policy"])
