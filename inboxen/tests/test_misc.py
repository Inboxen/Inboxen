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

from inboxen import models

class LastLoginTestCase(test.TestCase):
    """Test that last_login is not set"""
    fixtures = ['inboxen_testdata.json']

    def test_last_login(self):
        login = self.client.login(username="isdabizda", password="123456")
        self.assertEqual(login, True)

        user = models.User.objects.get(username="isdabizda")
        self.assertEqual(user.last_login, user.date_joined)
