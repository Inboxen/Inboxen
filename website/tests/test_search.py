# -*- coding: utf-8 -*-
##
#    Copyright (C) 2014, 2015 Jessica Tallon & Matt Molyneaux
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

import mock
import urllib

from django import test
from django.core import urlresolvers, cache

from inboxen.tests import factories


class SearchViewTestCase(test.TestCase):
    def setUp(self):
        super(SearchViewTestCase, self).setUp()
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456")
        self.url = urlresolvers.reverse("user-search", kwargs={"q": "cheddär"})
        key = "%s-cheddär" % self.user.id
        self.key = urllib.quote(key)

        if not login:
            raise Exception("Could not log in")

    def test_context(self):
        cache.cache.set(self.key, {"emails": [], "inboxes": []})
        response = self.client.get(self.url)
        self.assertIn("search_results", response.context)
        self.assertItemsEqual(response.context["search_results"], ["emails", "inboxes"])

    def test_content(self):
        cache.cache.set(self.key, {"emails": [], "inboxes": []})
        response = self.client.get(self.url)
        self.assertIn(u"There are no Inboxes or emails containing <em>cheddär</em>", response.content.decode("utf-8"))

        # this is bad, we shouldn't do this
        # TODO test the template directly
        with mock.patch("website.views.user.search.SearchView.get_queryset", return_value={}):
            response = self.client.get(self.url)
            self.assertIn(u'data-url="%s"' % urlresolvers.reverse("user-searchapi", kwargs={"q": "cheddär"}), response.content.decode("utf-8"))

    def test_get(self):
        cache.cache.set(self.key, {"emails": [], "inboxes": []})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
