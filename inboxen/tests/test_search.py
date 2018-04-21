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

from celery import exceptions
from django.core import urlresolvers, cache
from six.moves import urllib
from watson.models import SearchEntry

from inboxen.tests import factories
from inboxen.test import MockRequest, InboxenTestCase, override_settings


class SearchViewTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        self.url = urlresolvers.reverse("user-search", kwargs={"q": "cheddär"})
        key = "%s-None-None-cheddär" % self.user.id
        self.key = urllib.parse.quote(key)

        if not login:
            raise Exception("Could not log in")

    def test_context(self):
        cache.cache.set(self.key, {"results": []})
        response = self.client.get(self.url)
        self.assertIn("search_results", response.context)
        self.assertCountEqual(response.context["search_results"].keys(),
                              ["results", "has_next", "has_previous", "first", "last"])

    def test_content(self):
        cache.cache.set(self.key, {"results": []})
        response = self.client.get(self.url)
        self.assertIn(u"There are no Inboxes or emails containing <em>cheddär</em>", response.content.decode("utf-8"))

        # this is bad, we shouldn't do this
        # TODO test the template directly
        with mock.patch("inboxen.views.user.search.SearchView.get_queryset", return_value={}):
            response = self.client.get(self.url)
            self.assertIn(u'data-url="%s"' % urlresolvers.reverse(
                          "user-searchapi", kwargs={"q": "cheddär"}), response.content.decode("utf-8"))

    def test_get(self):
        cache.cache.set(self.key, {"results": []})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.views.user.search.watson_models.SearchEntry.objects.filter")
    @mock.patch("inboxen.views.user.search.tasks.search.apply_async")
    def test_get_task_run(self, task_mock, qs_mock):
        qs_mock.return_value = []
        task_mock.return_value.id = "abc"
        task_mock.return_value.get.side_effect = exceptions.TimeoutError

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(qs_mock.call_count, 0)
        self.assertEqual(task_mock.call_count, 1)
        self.assertEqual(task_mock.return_value.get.call_count, 1)

        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär"], "kwargs": {"before": None}}))
        self.assertCountEqual(response.context["search_results"], {})
        self.assertEqual(response.context["waiting"], True)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.views.user.search.tasks.search.apply_async")
    def test_get_cached_result(self, task_mock):
        factories.EmailFactory(inbox__user=self.user)

        task_mock.return_value.id = "abc"
        task_mock.return_value.get.side_effect = exceptions.TimeoutError

        cache.cache.set(self.key, {
            "results": list(SearchEntry.objects.values_list("id", flat=True)),
            "has_next": True,
            "has_previous": False,
            "first": "some-randomstring",
            "last": "somerandom-string",
        })

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(task_mock.call_count, 0)
        self.assertCountEqual(response.context["search_results"]["results"], SearchEntry.objects.all())
        self.assertEqual(response.context["search_results"]["has_next"], True)
        self.assertEqual(response.context["search_results"]["last"], "somerandom-string")
        self.assertEqual(response.context["search_results"]["has_previous"], False)
        self.assertEqual(response.context["search_results"]["first"], "some-randomstring")
        self.assertEqual(response.context["waiting"], False)

        cache.cache.set(self.key, {
            "results": [],
            "has_next": True,
            "has_previous": False,
            "first": "some-randomstring",
            "last": "somerandom-string",
        })

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(task_mock.call_count, 0)
        self.assertCountEqual(response.context["search_results"]["results"], [])
        self.assertEqual(response.context["search_results"]["has_next"], False)
        self.assertEqual(response.context["search_results"]["last"], None)
        self.assertEqual(response.context["search_results"]["has_previous"], False)
        self.assertEqual(response.context["search_results"]["first"], None)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.views.user.search.watson_models.SearchEntry.objects.filter")
    @mock.patch("inboxen.views.user.search.tasks.search.apply_async")
    def test_get_with_after_param(self, task_mock, qs_mock):
        qs_mock.return_value = []
        task_mock.return_value.id = "abc"
        task_mock.return_value.get.side_effect = exceptions.TimeoutError

        response = self.client.get(self.url + "?after=blahblah")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(qs_mock.call_count, 0)
        self.assertEqual(task_mock.call_count, 1)
        self.assertEqual(task_mock.return_value.get.call_count, 1)

        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär"],
                                                    "kwargs": {"after": "blahblah"}}))
        self.assertCountEqual(response.context["search_results"], {})

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.views.user.search.watson_models.SearchEntry.objects.filter")
    @mock.patch("inboxen.views.user.search.tasks.search.apply_async")
    def test_get_with_before_param(self, task_mock, qs_mock):
        qs_mock.return_value = []
        task_mock.return_value.id = "abc"
        task_mock.return_value.get.side_effect = exceptions.TimeoutError

        response = self.client.get(self.url + "?before=blahblah")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(qs_mock.call_count, 0)
        self.assertEqual(task_mock.call_count, 1)
        self.assertEqual(task_mock.return_value.get.call_count, 1)

        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär"],
                                                    "kwargs": {"before": "blahblah"}}))
        self.assertCountEqual(response.context["search_results"], {})

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.views.user.search.watson_models.SearchEntry.objects.filter")
    @mock.patch("inboxen.views.user.search.tasks.search.apply_async")
    def test_get_with_before_and_after_param(self, task_mock, qs_mock):
        qs_mock.return_value = []
        task_mock.return_value.id = "abc"
        task_mock.return_value.get.side_effect = exceptions.TimeoutError

        response = self.client.get(self.url + "?after=blahblah&before=bluhbluh")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(qs_mock.call_count, 0)
        self.assertEqual(task_mock.call_count, 1)
        self.assertEqual(task_mock.return_value.get.call_count, 1)

        # before param should be ignored, task will raise an error otherwise
        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär"],
                                                    "kwargs": {"after": "blahblah"}}))
        self.assertCountEqual(response.context["search_results"], {})

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.views.user.search.AsyncResult")
    def test_task_running(self, result_mock):
        cache.cache.set(self.key, {"task": "blahblahblah"})
        result_mock.return_value.get.side_effect = exceptions.TimeoutError

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["waiting"], True)

        self.assertEqual(result_mock.call_count, 1)
        self.assertEqual(result_mock.call_args, (("blahblahblah",), {}))

    def test_no_query(self):
        url = urlresolvers.reverse("user-search")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["waiting"], False)


class SearchApiViewTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        self.url = urlresolvers.reverse("user-searchapi", kwargs={"q": "cheddär"})
        key = "%s-None-None-cheddär" % self.user.id
        self.key = urllib.parse.quote(key)

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
    @mock.patch("inboxen.views.user.search.AsyncResult")
    def test_search_running_but_finishes_within_timeout(self, result_mock):
        cache.cache.set(self.key, {"task": "blahblahblah"})

        response = self.client.head(self.url)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(result_mock.call_count, 1)
        self.assertEqual(result_mock.call_args, (("blahblahblah",), {}))

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.views.user.search.AsyncResult")
    def test_search_running_and_timeout(self, result_mock):
        result_mock.return_value.get.side_effect = exceptions.TimeoutError
        cache.cache.set(self.key, {"task": "blahblahblah"})

        response = self.client.head(self.url)
        self.assertEqual(response.status_code, 202)

        self.assertEqual(result_mock.call_count, 1)
        self.assertEqual(result_mock.call_args, (("blahblahblah",), {}))
