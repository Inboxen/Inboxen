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

from unittest import mock

from celery import exceptions
from django import urls
from django.conf import settings as dj_settings
from django.core.cache import cache
from django.test import override_settings

from inboxen import models
from inboxen.search.utils import create_search_cache_key
from inboxen.test import InboxenTestCase, MockRequest
from inboxen.tests import factories
import inboxen


class HomeViewTestCase(InboxenTestCase):
    def setUp(self):
        super(HomeViewTestCase, self).setUp()
        self.user = factories.UserFactory()
        domain = factories.DomainFactory()
        self.inboxes = factories.InboxFactory.create_batch(30, domain=domain, user=self.user)

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urls.reverse("user-home")

    def test_context(self):
        response = self.client.get(self.get_url())
        context_settings = response.context['settings']

        # test that something is getting set
        self.assertEqual(dj_settings.SITE_NAME, context_settings["SITE_NAME"])

        # test that INBOXEN_COMMIT_ID is actually working
        self.assertEqual(context_settings["INBOXEN_COMMIT_ID"], inboxen.__version__)

        # Please add any settings that may contain passwords or secrets:
        self.assertNotIn("SECRET_KEY", context_settings)
        self.assertNotIn("DATABASES", context_settings)

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_pinned_first(self):
        # Mark some specific inboxes based on activity. One for most recent, one
        # in the middel and then the least recent.
        ordered_inboxes = models.Inbox.objects.all().add_last_activity()
        ordered_inboxes = ordered_inboxes.order_by("-last_activity")

        # Most recent activity
        latest = ordered_inboxes[0]
        latest.pinned = True
        latest.save()

        # Around (or exactly) the middle in activity.
        middle = ordered_inboxes[int(len(ordered_inboxes) / 2)]
        middle.pinned = True
        middle.save()

        # Finally the least active (NB: negative indexing isn't supported).
        least = ordered_inboxes[len(ordered_inboxes)-1]
        least.pinned = True
        least.save()

        response = self.client.get(self.get_url())
        objs = response.context["page_obj"].object_list[:5]

        # Check the top inboxes three inboxes are pinned.
        self.assertEqual(
            [obj.pinned for obj in objs],
            [True, True, True, False, False]
        )

        # Check the pinned inboxes are ordered amongst themselves.
        self.assertEqual(
            [obj.id for obj in objs][:3],
            [latest.id, middle.id, least.id]
        )

    def test_disabled_sink(self):
        """ Check disabled inboxes sink to the bottom """
        # Find three inboxes, the inbox with: the most recent activity, least
        # recent activity and then pick one from the middle. This insures that
        # they sink to the bottom but keep their order within the disabled.
        ordered_inboxes = models.Inbox.objects.all().add_last_activity()
        ordered_inboxes = ordered_inboxes.order_by("-last_activity")

        # The inbox with the latest activity.
        latest = ordered_inboxes[0]
        latest.disabled = True
        latest.save()

        # One from the middle
        middle = ordered_inboxes[int(len(ordered_inboxes) / 2)]
        middle.disabled = True
        middle.save()

        # Finally the least active (NB: negative indexing isn't supported).
        least = ordered_inboxes[len(ordered_inboxes)-1]
        least.disabled = True
        least.save()

        # Get the page, they should have been pushed to the second page.
        response = self.client.get(self.get_url() + "2/")
        objs = response.context["page_obj"].object_list

        # Check the last three are disabled
        self.assertEqual(
            [obj.disabled for obj in objs],
            [False, False, True, True, True]
        )

        # Check the three are in order amongst themselves.
        self.assertEqual(
            [obj.id for obj in objs[2:]],
            [latest.id, middle.id, least.id]
        )

    def test_pagin(self):
        # there should be 30 inboxes in the test fixtures
        # and pages are paginated by 25 items
        response = self.client.get(self.get_url() + "2/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.get_url() + "3/")
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        inbox = self.inboxes[0]
        was_pinned = inbox.pinned

        # pin
        response = self.client.post(self.get_url(), {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 302)

        inbox.refresh_from_db()
        self.assertNotEqual(inbox.pinned, was_pinned)

        # toggle
        response = self.client.post(self.get_url(), {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 302)

        inbox.refresh_from_db()
        self.assertEqual(inbox.pinned, was_pinned)

        # invalid
        response = self.client.post(self.get_url(), {"pin-inbox": "aagfdsgsfdg"})
        self.assertEqual(response.status_code, 404)

        # disabled
        inbox.disabled = True
        inbox.save()
        response = self.client.post(self.get_url(), {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 404)

    def test_post_form_view(self):
        url = urls.reverse("form-home")

        inbox = self.inboxes[0]
        was_pinned = inbox.pinned

        # pin
        response = self.client.post(url, {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 204)

        inbox.refresh_from_db()
        self.assertNotEqual(inbox.pinned, was_pinned)

        # toggle
        response = self.client.post(url, {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 204)

        inbox.refresh_from_db()
        self.assertEqual(inbox.pinned, was_pinned)

        # invalid
        response = self.client.post(url, {"pin-inbox": "aagfdsgsfdg"})
        self.assertEqual(response.status_code, 404)

        # disabled
        inbox.disabled = True
        inbox.save()
        response = self.client.post(url, {"pin-inbox": str(inbox)})
        self.assertEqual(response.status_code, 404)


class SearchViewTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        self.url = urls.reverse("user-home-search", kwargs={"q": "cheddär"})
        self.key = create_search_cache_key(self.user.id, "cheddär", models.Inbox._meta.label, None, None)

        if not login:
            raise Exception("Could not log in")

    def test_context(self):
        cache.set(self.key, {"results": []})
        response = self.client.get(self.url)
        self.assertIn("waiting", response.context)
        self.assertNotIn("has_next", response.context)
        self.assertNotIn("has_previous", response.context)
        self.assertNotIn("last", response.context)
        self.assertNotIn("first", response.context)

    def test_content(self):
        cache.set(self.key, {"results": []})
        response = self.client.get(self.url)
        self.assertIn(u"No inboxes found containing <i>cheddär</i>", response.content.decode("utf-8"))

    def test_get(self):
        cache.set(self.key, {"results": []})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.search.views.tasks.search.apply_async")
    def test_get_task_run(self, task_mock):
        task_mock.return_value.id = "abc"
        task_mock.return_value.get.side_effect = exceptions.TimeoutError

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(task_mock.call_count, 1)
        self.assertEqual(task_mock.return_value.get.call_count, 1)

        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär", "inboxen.Inbox"],
                                                    "kwargs": {"before": None}}))
        self.assertEqual(response.context["waiting"], True)
        self.assertNotIn("has_next", response.context)
        self.assertNotIn("has_previous", response.context)
        self.assertNotIn("last", response.context)
        self.assertNotIn("first", response.context)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.search.views.tasks.search.apply_async")
    def test_get_cached_result(self, task_mock):
        inbox = factories.InboxFactory(user=self.user)

        task_mock.return_value.id = "abc"
        task_mock.return_value.get.side_effect = exceptions.TimeoutError

        cache.set(self.key, {
            "results": [inbox.id],
            "has_next": True,
            "has_previous": False,
            "first": "some-randomstring",
            "last": "somerandom-string",
        })

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(task_mock.call_count, 0)
        self.assertEqual(response.context["has_next"], True)
        self.assertEqual(response.context["last"], "somerandom-string")
        self.assertEqual(response.context["has_previous"], False)
        self.assertEqual(response.context["first"], "some-randomstring")
        self.assertEqual(response.context["waiting"], False)

        cache.set(self.key, {
            "results": [],
            "has_next": True,
            "has_previous": False,
            "first": "some-randomstring",
            "last": "somerandom-string",
        })

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(task_mock.call_count, 0)
        self.assertEqual(response.context["waiting"], False)
        self.assertNotIn("has_next", response.context)
        self.assertNotIn("has_previous", response.context)
        self.assertNotIn("first", response.context)
        self.assertNotIn("last", response.context)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.search.views.tasks.search.apply_async")
    def test_get_with_after_param(self, task_mock):
        task_mock.return_value.id = "abc"
        task_mock.return_value.get.side_effect = exceptions.TimeoutError

        response = self.client.get(self.url + "?after=blahblah")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(task_mock.call_count, 1)
        self.assertEqual(task_mock.return_value.get.call_count, 1)

        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär", "inboxen.Inbox"],
                                                    "kwargs": {"after": "blahblah"}}))
        self.assertEqual(response.context["waiting"], True)
        self.assertNotIn("has_next", response.context)
        self.assertNotIn("has_previous", response.context)
        self.assertNotIn("last", response.context)
        self.assertNotIn("first", response.context)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.search.views.tasks.search.apply_async")
    def test_get_with_before_param(self, task_mock):
        task_mock.return_value.id = "abc"
        task_mock.return_value.get.side_effect = exceptions.TimeoutError

        response = self.client.get(self.url + "?before=blahblah")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(task_mock.call_count, 1)
        self.assertEqual(task_mock.return_value.get.call_count, 1)

        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär", "inboxen.Inbox"],
                                                    "kwargs": {"before": "blahblah"}}))
        self.assertEqual(response.context["waiting"], True)
        self.assertNotIn("has_next", response.context)
        self.assertNotIn("has_previous", response.context)
        self.assertNotIn("last", response.context)
        self.assertNotIn("first", response.context)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.search.views.tasks.search.apply_async")
    def test_get_with_before_and_after_param(self, task_mock):
        task_mock.return_value.id = "abc"
        task_mock.return_value.get.side_effect = exceptions.TimeoutError

        response = self.client.get(self.url + "?after=blahblah&before=bluhbluh")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(task_mock.call_count, 1)
        self.assertEqual(task_mock.return_value.get.call_count, 1)

        # before param should be ignored, task will raise an error otherwise
        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär", "inboxen.Inbox"],
                                                    "kwargs": {"after": "blahblah"}}))
        self.assertEqual(response.context["waiting"], True)
        self.assertNotIn("has_next", response.context)
        self.assertNotIn("has_previous", response.context)
        self.assertNotIn("last", response.context)
        self.assertNotIn("first", response.context)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    @mock.patch("inboxen.search.views.AsyncResult")
    def test_task_running(self, result_mock):
        cache.set(self.key, {"task": "blahblahblah"})
        result_mock.return_value.get.side_effect = exceptions.TimeoutError

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["waiting"], True)

        self.assertEqual(result_mock.call_count, 1)
        self.assertEqual(result_mock.call_args, (("blahblahblah",), {}))

    def test_no_query(self):
        url = urls.reverse("user-home-search")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["waiting"], False)
