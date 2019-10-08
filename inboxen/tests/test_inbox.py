# -*- coding: utf-8 -*-
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
import itertools
import warnings

from celery import exceptions
from django import urls
from django.conf import settings
from django.core.cache import cache
from django.test import override_settings

from inboxen import forms as inboxen_forms
from inboxen import models
from inboxen.search.utils import create_search_cache_key
from inboxen.test import InboxenTestCase, MockRequest
from inboxen.tests import factories
from inboxen.utils.ratelimit import inbox_ratelimit


class InboxTestAbstract(object):
    """An abstract TestCase that won't get picked up by Django's test finder"""
    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_post_important(self):
        count = models.Email.objects.filter(important=True).count()
        self.assertEqual(count, 0)

        params = {"important": ""}

        for email in self.emails[:2]:
            params[email.eid] = "email"

        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)

        count = models.Email.objects.filter(important=True).count()
        self.assertEqual(count, 2)

        # and then mark them as unimportant again
        params = {"unimportant": ""}

        for email in self.emails[:2]:
            params[email.eid] = "email"

        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)

        count = models.Email.objects.filter(important=True).count()
        self.assertEqual(count, 0)

    def test_get_read(self):
        count = models.Email.objects.filter(read=True).count()
        self.assertEqual(count, 0)

        for email in self.emails[:2]:
            kwargs = {
                "inbox": email.inbox.inbox,
                "domain": email.inbox.domain.domain,
                "id": email.eid,
            }
            self.client.get(urls.reverse("email-view", kwargs=kwargs))

        count = models.Email.objects.filter(read=True).count()
        self.assertEqual(count, 2)

    def test_post_delete(self):
        count_1st = len(self.emails) + 1  # my emails, plus one that's not mine

        params = dict([(email.eid, "email") for email in self.emails[:10]])
        params[self.not_mine.eid] = "email"  # this email should get ignored
        params["delete"] = ""
        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)

        count_2nd = models.Email.objects.count()
        self.assertEqual(count_1st - 10, count_2nd)

    def test_post_single_delete(self):
        email = self.emails[0]
        response = self.client.post(self.get_url(), {"delete-single": email.eid})
        self.assertEqual(response.status_code, 302)

        # second time around, it's already deleted but we don't want an error
        response = self.client.post(self.get_url(), {"delete-single": email.eid})
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(models.Email.DoesNotExist):
            models.Email.objects.get(id=email.id)

    def test_post_single_important(self):
        email = self.emails[0]
        response = self.client.post(self.get_url(), {"important-single": email.eid})
        self.assertEqual(response.status_code, 302)
        email.refresh_from_db()
        self.assertTrue(email.important)

        response = self.client.post(self.get_url(), {"important-single": email.eid})
        self.assertEqual(response.status_code, 302)
        email.refresh_from_db()
        self.assertFalse(email.important)

    def test_important_first(self):
        # mark some emails as important
        for email in self.emails[:3]:
            email.important = True
            email.save()

        response = self.client.get(self.get_url())
        objs = response.context["page_obj"].object_list[:5]

        self.assertEqual(
            [obj.important for obj in objs],
            [True, True, True, False, False]
        )

    def test_pagin(self):
        # there should be 30 emails in the test fixtures
        # and pages are paginated by 25 items
        response = self.client.get(self.get_url() + "2/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.get_url() + "3/")
        self.assertEqual(response.status_code, 404)


class SingleInboxTestCase(InboxTestAbstract, InboxenTestCase):
    """Test Inbox specific views"""
    def setUp(self):
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

        self.inbox = factories.InboxFactory(user=self.user)
        self.emails = factories.EmailFactory.create_batch(30, inbox=self.inbox)
        self.not_mine = factories.EmailFactory.create(inbox__user=self.user)

        for email in self.emails:
            part = factories.PartListFactory(email=email)
            factories.HeaderFactory(part=part)
            factories.HeaderFactory(part=part, name="From")
            factories.HeaderFactory(part=part, name="Subject")

    def get_url(self):
        return urls.reverse("single-inbox",
                            kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})


class UnifiedInboxTestCase(InboxTestAbstract, InboxenTestCase):
    """Test Unified Inbox specific views"""
    def setUp(self):
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

        self.emails = factories.EmailFactory.create_batch(30, inbox__user=self.user)
        self.not_mine = factories.EmailFactory.create()

        for email in self.emails:
            part = factories.PartListFactory(email=email)
            factories.HeaderFactory(part=part, name="From")
            factories.HeaderFactory(part=part, name="Subject")

    def get_url(self):
        return urls.reverse("unified-inbox")


class InboxAddTestCase(InboxenTestCase):
    """Test the add inbox page"""
    def setUp(self):
        """Create the client and grab the user"""
        self.user = factories.UserFactory()
        self.other_user = factories.UserFactory(username="lalna")

        for args in itertools.product([True, False], [self.user, self.other_user, None]):
            factories.DomainFactory(enabled=args[0], owner=args[1])

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urls.reverse("inbox-add")

    def test_inbox_add_form(self):
        form = inboxen_forms.InboxAddForm(MockRequest(self.user))

        self.assertNotIn("inbox", form.fields)
        self.assertIn("domain", form.fields)
        self.assertIn("description", form.fields)

        for domain in form.fields["domain"].queryset:
            self.assertTrue(domain.enabled)
            self.assertTrue(domain.owner is None or domain.owner.id == self.user.id)

        # vaid domain
        domain_id = form.fields["domain"].queryset[0].id
        form_data = {"domain": domain_id, "description": "hello"}
        form = inboxen_forms.InboxAddForm(MockRequest(self.user), data=form_data)
        self.assertTrue(form.is_valid())

        # invalid domain
        domain_id = models.Domain.objects.filter(enabled=False)[0].id
        form_data = {"domain": domain_id, "description": "hello"}
        form = inboxen_forms.InboxAddForm(MockRequest(self.user), data=form_data)
        self.assertFalse(form.is_valid())

        # null in description
        domain_id = models.Domain.objects.filter(enabled=True)[0].id
        form_data = {"domain": domain_id, "description": "hello\x00null"}
        form = inboxen_forms.InboxAddForm(MockRequest(self.user), data=form_data)
        self.assertFalse(form.is_valid())

    def test_inbox_add(self):
        response = self.client.get(self.get_url())
        self.assertIsInstance(response.context["form"], inboxen_forms.InboxAddForm)

        domain = models.Domain.objects.filter(enabled=True, owner=None)[0]
        inbox_count_1st = models.Inbox.objects.count()
        response = self.client.post(self.get_url(), {"domain": domain.id, "description": "nothing at all"})
        self.assertEqual(response.status_code, 302)

        inbox_count_2nd = models.Inbox.objects.count()
        self.assertEqual(inbox_count_1st, inbox_count_2nd - 1)

        new_inbox = models.Inbox.objects.first()
        self.assertEqual(new_inbox.description, "nothing at all")
        self.assertEqual(new_inbox.user, self.user)
        self.assertEqual(new_inbox.domain, domain)
        self.assertNotEqual(new_inbox.search_tsv, None)

    def test_inbox_ratelimit(self):
        domain = models.Domain.objects.filter(enabled=True, owner=None)[0]
        counter = 0

        for i in range(200):
            response = self.client.post(self.get_url(), {"domain": domain.id})
            counter += 1
            if response.status_code == 200:
                break

        self.assertEqual(counter, settings.INBOX_LIMIT_COUNT + 1)
        self.assertEqual(models.Inbox.objects.count(), settings.INBOX_LIMIT_COUNT)

        # check that changing username does not affect this counter
        self.user.username = self.user.username + "1"
        self.user.save()

        response = self.client.post(self.get_url(), {"domain": domain.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Inbox.objects.count(), settings.INBOX_LIMIT_COUNT)

        # login the other user and check that they can still create inboxes
        assert self.client.login(username=self.other_user.username, password="123456", request=MockRequest(self.user))

        response = self.client.post(self.get_url(), {"domain": domain.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.Inbox.objects.count(), settings.INBOX_LIMIT_COUNT + 1)

    def test_inbox_ratelimit_valid_keys(self):
        request = MockRequest(self.user)

        cache_prefix = u"hello€@.+-_ <>"

        with override_settings(INBOX_LIMIT_CACHE_PREFIX=cache_prefix), \
                warnings.catch_warnings(record=True) as w:
            self.assertEqual(inbox_ratelimit.counter_full(request), False)

            for i in range(settings.INBOX_LIMIT_COUNT + 1):
                inbox_ratelimit.counter_increase(request)

            self.assertEqual(inbox_ratelimit.counter_full(request), True)

        self.assertEqual(len(w), 0)


class InboxAddInlineTestCase(InboxenTestCase):
    """Test the add inbox inline form page"""
    def setUp(self):
        """Create the client and grab the user"""
        self.user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        for args in itertools.product([True, False], [self.user, other_user, None]):
            factories.DomainFactory(enabled=args[0], owner=args[1])

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urls.reverse("form-inbox-add")

    def test_inbox_add(self):
        response = self.client.get(self.get_url())
        self.assertIsInstance(response.context["form"], inboxen_forms.InboxAddForm)

        domain = models.Domain.objects.filter(enabled=True, owner=None)[0]
        inbox_count_1st = models.Inbox.objects.count()
        response = self.client.post(self.get_url(), {"domain": domain.id, "description": "nothing at all"})
        self.assertEqual(response.status_code, 204)

        inbox_count_2nd = models.Inbox.objects.count()
        self.assertEqual(inbox_count_1st, inbox_count_2nd - 1)

        new_inbox = models.Inbox.objects.first()
        self.assertEqual(new_inbox.description, "nothing at all")
        self.assertEqual(new_inbox.user, self.user)
        self.assertEqual(new_inbox.domain, domain)
        self.assertNotEqual(new_inbox.search_tsv, None)


class InboxEditTestCase(InboxenTestCase):
    """Test the edit inbox page"""
    def setUp(self):
        """Create the client and grab the user"""
        super(InboxEditTestCase, self).setUp()
        self.user = factories.UserFactory()
        self.inbox = factories.InboxFactory(user=self.user)

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urls.reverse("inbox-edit",
                            kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})

    def test_inbox_form(self):
        response = self.client.get(self.get_url())
        form = response.context["form"]
        self.assertIsInstance(form, inboxen_forms.InboxEditForm)

        self.assertNotIn("inbox", form.fields)
        self.assertNotIn("domain", form.fields)
        self.assertIn("description", form.fields)

    def test_inbox_add_description(self):
        response = self.client.post(self.get_url(), {"description": "nothing\x00 at all"})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.get_url(), {"description": "nothing at all"})
        self.assertEqual(response.status_code, 302)

        inbox = models.Inbox.objects.filter(description="nothing at all").first()
        self.assertEqual(inbox.id, self.inbox.id)
        # search index updated
        self.assertNotEqual(inbox.search_tsv, self.inbox.search_tsv)

    def test_not_found(self):
        url = urls.reverse("inbox-edit", kwargs={"inbox": "test", "domain": "example.com"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class InboxInlineEditTestCase(InboxenTestCase):
    """Test the inline version of the inbox edit page"""
    def setUp(self):
        """Create the client and grab the user"""
        super(InboxInlineEditTestCase, self).setUp()
        self.user = factories.UserFactory()
        self.inbox = factories.InboxFactory(user=self.user)

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urls.reverse("form-inbox-edit",
                            kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})

    def test_inbox_form(self):
        response = self.client.get(self.get_url())
        form = response.context["form"]
        self.assertIsInstance(form, inboxen_forms.InboxEditForm)

        self.assertNotIn("inbox", form.fields)
        self.assertNotIn("domain", form.fields)
        self.assertIn("description", form.fields)

    def test_inbox_add_description(self):
        response = self.client.post(self.get_url(), {"description": "nothing\x00 at all"})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.get_url(), {"description": "nothing at all"})
        self.assertEqual(response.status_code, 204)

        inbox = models.Inbox.objects.filter(description="nothing at all").first()
        self.assertEqual(inbox.id, self.inbox.id)
        # search index updated
        self.assertNotEqual(inbox.search_tsv, self.inbox.search_tsv)

    def test_not_found(self):
        url = urls.reverse("form-inbox-edit", kwargs={"inbox": "test", "domain": "example.com"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class InboxEmailEditTestCase(InboxenTestCase):
    """Test the post only email edit view"""
    def setUp(self):
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

        self.inbox = factories.InboxFactory(user=self.user)
        self.emails = factories.EmailFactory.create_batch(30, inbox=self.inbox)
        self.not_mine = factories.EmailFactory.create(inbox__user=self.user)

        for email in self.emails:
            part = factories.PartListFactory(email=email)
            factories.HeaderFactory(part=part)
            factories.HeaderFactory(part=part, name="From")
            factories.HeaderFactory(part=part, name="Subject")

    def get_url(self):
        return urls.reverse("form-inbox-email")

    def test_no_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 405)

    def test_post_important(self):
        count = models.Email.objects.filter(important=True).count()
        self.assertEqual(count, 0)

        params = {"important": ""}

        for email in self.emails[:2]:
            params[email.eid] = "email"

        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 204)

        count = models.Email.objects.filter(important=True).count()
        self.assertEqual(count, 2)

        # and then mark them as unimportant again
        params = {"unimportant": ""}

        for email in self.emails[:2]:
            params[email.eid] = "email"

        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 204)

        count = models.Email.objects.filter(important=True).count()
        self.assertEqual(count, 0)

    def test_post_delete(self):
        count_1st = len(self.emails)
        params = dict([(email.eid, "email") for email in self.emails[:10]])
        params[self.not_mine.eid] = "email"  # this email should get ignored
        params["delete"] = ""
        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 204)

        count_2nd = models.Email.objects.count()
        self.assertEqual(count_1st - 10, count_2nd)

    def test_post_single_delete(self):
        email = self.emails[0]
        response = self.client.post(self.get_url(), {"delete-single": email.eid})
        self.assertEqual(response.status_code, 204)

        # second time around, throw a 404
        response = self.client.post(self.get_url(), {"delete-single": email.eid})
        self.assertEqual(response.status_code, 404)

        with self.assertRaises(models.Email.DoesNotExist):
            models.Email.objects.get(id=email.id)

    def test_post_single_important(self):
        email = self.emails[0]
        response = self.client.post(self.get_url(), {"important-single": email.eid})
        self.assertEqual(response.status_code, 204)
        email.refresh_from_db()
        self.assertTrue(email.important)

        response = self.client.post(self.get_url(), {"important-single": email.eid})
        self.assertEqual(response.status_code, 204)
        email.refresh_from_db()
        self.assertFalse(email.important)


class InboxDeleteTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))
        assert login

        self.inbox = factories.InboxFactory(user=self.user)
        self.url = urls.reverse("inbox-disown",
                                kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})

    @mock.patch("inboxen.forms.inbox.disown_inbox")
    def test_get(self, task_mock):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(task_mock.delay.call_count, 0)

    @mock.patch("inboxen.forms.inbox.disown_inbox")
    def test_get_404(self, task_mock):
        self.inbox.user = None
        self.inbox.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(task_mock.delay.call_count, 0)

    @mock.patch("inboxen.forms.inbox.disown_inbox")
    def test_post_valid(self, task_mock):
        response = self.client.post(self.url, {"disown": 1})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urls.reverse("user-home"))

        self.assertEqual(task_mock.delay.call_count, 1)
        self.assertEqual(task_mock.delay.call_args, ((self.inbox.id,),))

    @mock.patch("inboxen.forms.inbox.disown_inbox")
    def test_post_invalid(self, task_mock):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(task_mock.delay.call_count, 0)


class SearchViewTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory()
        self.inbox = factories.InboxFactory(user=self.user)

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        self.url = urls.reverse("single-inbox-search", kwargs={"q": "cheddär",
                                                               "inbox": self.inbox.inbox,
                                                               "domain": self.inbox.domain.domain})
        self.key = create_search_cache_key(self.user.id, "cheddär", models.Email._meta.label, None, None)

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
        self.assertIn(u"No emails containing <i>cheddär</i>",
                      response.content.decode("utf-8"))

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

        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär", "inboxen.Email"],
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

        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär", "inboxen.Email"],
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

        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär", "inboxen.Email"],
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
        self.assertEqual(task_mock.call_args, ((), {"args": [self.user.id, u"cheddär", "inboxen.Email"],
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
        url = urls.reverse("single-inbox-search", kwargs={
            "inbox": self.inbox.inbox,
            "domain": self.inbox.domain.domain,
        })

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["waiting"], False)
