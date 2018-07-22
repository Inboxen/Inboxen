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

from django.urls import reverse

from inboxen.test import InboxenTestCase, MockRequest, grant_otp, grant_sudo
from inboxen.tests import factories


class OtpTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def test_sudo_required(self):
        urls = [
            reverse("user-twofactor-setup"),
            reverse("user-twofactor-backup"),
            reverse("user-twofactor-disable"),
            reverse("user-twofactor-qrcode"),
        ]

        grant_otp(self.client, self.user)

        for url in urls:
            response = self.client.get(url)
            try:
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response["Location"], "{}?next={}".format(reverse("user-sudo"), url))
            except AssertionError as exp:
                raise AssertionError("{} did not redirect correcrlty: {}".format(url, exp))

        grant_sudo(self.client)

        for url in urls:
            response = self.client.get(url)
            try:
                self.assertIn(response.status_code, [200, 404])
            except AssertionError as exp:
                raise AssertionError("{} did not give an expected response code: {}".format(url, exp))

    def test_otp_required(self):
        urls = [
            reverse("user-twofactor-backup"),
            reverse("user-twofactor-disable"),
        ]

        grant_sudo(self.client)

        for url in urls:
            response = self.client.get(url)
            try:
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response["Location"], "{}?next={}".format(reverse("user-login"), url))
            except AssertionError as exp:
                raise AssertionError("{} did not give an expected response code: {}".format(url, exp))


class SetupTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def test_missing_mgmt_data(self):
        grant_sudo(self.client)

        good_data = {
            "two_factor_setup_view-current_step": "generator",
            "generator-token": "123456",
        }

        response = self.client.post(reverse("user-twofactor-setup"), good_data)
        # form was validated and *form* errors returned
        self.assertEqual(response.status_code, 200)

        bad_data = {
            "generator-token": "123456",
        }
        response = self.client.post(reverse("user-twofactor-setup"), bad_data)
        # Bad request, but no exception generated
        self.assertEqual(response.status_code, 400)
