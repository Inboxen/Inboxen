##
#    Copyright (C) 2017 Jessica Tallon & Matt Molyneaux
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
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test.client import RequestFactory
import mock

from cms.decorators import is_secure_admin
from inboxen.tests.factories import UserFactory
from inboxen.tests.utils import MockRequest


@is_secure_admin
def test_view(requset):
    return HttpResponse()


class IsSecureAdminTestCase(test.TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_is_secure_admin(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)
        self.user.is_superuser = True

        response = test_view(request)
        self.assertEqual(response.status_code, 200)

    def test_no_sudo(self):
        request = MockRequest(self.user, has_otp=True)
        self.user.is_superuser = True

        response = test_view(request)
        self.assertEqual(response.status_code, 302)

    def test_not_admin(self):
        request = MockRequest(self.user, has_otp=True, has_sudo=True)

        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_no_otp(self):
        request = MockRequest(self.user, has_sudo=True)
        self.user.is_superuser = True

        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_is_anon(self):
        request = MockRequest(AnonymousUser())

        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_together(self):
        # don't test response per se, just make sure all combinations of tests
        # produce a negative response

        # test view
        @is_secure_admin
        def test_view(requset):
            return HttpResponse()

        # helper functions to set various things on the request object

        def setup_request(request):
            request.user.is_superuser = False
            request.user.is_verified.return_value = False
            request.is_sudo.return_value = False

        def noop(requset):
            pass

        def set_superuser(request):
            request.user.is_superuser = True

        def set_otp(requset):
            request.user.is_verified.return_value = True

        def set_sudo(request):
            request.is_sudo.return_value = True

        # collect fiunctions and then add them together in all possible combinations
        funcs = [set_superuser, set_otp, set_sudo]
        factors = [[f, noop] for f in funcs]
        products = itertools.product(*factors)

        for superuser, otp, sudo in products:
            request = mock.Mock()

            setup_request(request)
            superuser(request)
            otp(request)
            sudo(request)

            response = None
            exception_raised = False
            try:
                response = test_view(request)
            except PermissionDenied:
                exception_raised = True

            chosen_funcs = [superuser, otp, sudo]
            if chosen_funcs == funcs:
                # special case where everything went fine
                self.assertEqual(response.status_code, 200, "Reponse code was not 200: %r" % chosen_funcs)
            elif response is None:
                self.assertTrue(exception_raised, "Response was None, but no PermissionDenied was raised: %r" % chosen_funcs)
            else:
                self.assertNotEqual(response.status_code, 200, "Response code was 200: %r" % chosen_funcs)
