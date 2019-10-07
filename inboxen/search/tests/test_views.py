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

from unittest import mock

from celery import exceptions
from django import urls
from django.core import cache
from django.test import override_settings

from inboxen.search.utils import create_search_cache_key
from inboxen.test import InboxenTestCase, MockRequest
from inboxen.tests import factories


class SearchApiViewTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        self.key = create_search_cache_key(self.user.id, "cheddår", None, None)
        self.url = "%s?token=%s" % (
            urls.reverse("search:api"),
            self.key,
        )

        if not login:
            raise Exception("Could not log in")

    def test_no_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_no_search_is_running(self):
        response = self.client.head(self.url)
        self.assertEqual(response.status_code, 400)

    def test_search_finished(self):
        cache.cache.set(self.key, {"results": []})

        response = self.client.head(self.url)
        self.assertEqual(response.status_code, 201)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.search.views.AsyncResult")
    def test_search_running_but_finishes_within_timeout(self, result_mock):
        cache.cache.set(self.key, {"task": "blahblahblah"})

        response = self.client.head(self.url)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(result_mock.call_count, 1)
        self.assertEqual(result_mock.call_args, (("blahblahblah",), {}))

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.search.views.AsyncResult")
    def test_search_running_and_timeout(self, result_mock):
        result_mock.return_value.get.side_effect = exceptions.TimeoutError
        cache.cache.set(self.key, {"task": "blahblahblah"})

        response = self.client.head(self.url)
        self.assertEqual(response.status_code, 202)

        self.assertEqual(result_mock.call_count, 1)
        self.assertEqual(result_mock.call_args, (("blahblahblah",), {}))
