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
from django.core.urlresolvers import reverse


class TosViewsTestCase(test.TestCase):
    def test_get(self):
        response = self.client.get(reverse("termsofservice-index"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("termsofservice-tos"))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse("termsofservice-who"))
        self.assertEqual(response.status_code, 200)
