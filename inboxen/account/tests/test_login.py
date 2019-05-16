##
#    Copyright (C) 2018 Jessica Tallon & Matt Molyneaux
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

from django import urls

from inboxen.test import InboxenTestCase


class LoginTestCase(InboxenTestCase):
    def test_missing_mgmt_data(self):
        good_data = {
            "auth-username": "user1",
            "auth-password": "pass1",
            "login_view-current_step": "auth",
        }

        response = self.client.post(urls.reverse("user-login"), good_data)
        # form was validated and *form* errors returned
        self.assertEqual(response.status_code, 200)

        bad_data = {
            "auth-username": "user1",
            "auth-password": "pass1",
        }
        response = self.client.post(urls.reverse("user-login"), bad_data)
        # Bad request, but no exception generated
        self.assertEqual(response.status_code, 400)
