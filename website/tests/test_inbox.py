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

import itertools

from django import test
from django.conf import settings
from django.core import urlresolvers
from django.utils import unittest

from inboxen import models
from inboxen.tests import factories
from website import forms as inboxen_forms
from website.tests.utils import MockRequest


class InboxTestAbstract(object):
    """An abstract TestCase that won't get picked up by Django's test finder"""
    def setUp(self):
        """Create the client and grab the user"""
        super(InboxTestAbstract, self).setUp()
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_post_important(self):
        count = models.Email.objects.filter(flags=models.Email.flags.important).count()
        self.assertEqual(count, 0)

        params = {"important": ""}

        for email in self.emails[:2]:
            params[email.eid] = "email"

        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)

        count = models.Email.objects.filter(flags=models.Email.flags.important).count()
        self.assertEqual(count, 2)

    def test_get_read(self):
        count = models.Email.objects.filter(flags=models.Email.flags.read).count()
        self.assertEqual(count, 0)

        for email in self.emails[:2]:
            kwargs = {
                "inbox": email.inbox.inbox,
                "domain": email.inbox.domain.domain,
                "id": email.eid,
            }
            self.client.get(urlresolvers.reverse("email-view", kwargs=kwargs))

        count = models.Email.objects.filter(flags=models.Email.flags.read).count()
        self.assertEqual(count, 2)

    @unittest.skipIf(settings.CELERY_ALWAYS_EAGER, "Task errors during testing, works fine in production")
    def test_post_delete(self):
        count_1st = len(self.emails)

        params = dict([(email.id, "email") for email in self.emails[:10]])
        params["delete"] = ""
        response = self.client.post(self.get_url(), params)
        self.assertEqual(response.status_code, 302)

        count_2nd = models.Email.objects.count()
        self.assertEqual(count_1st - 10, count_2nd)

    def test_post_single_delete(self):
        email_id = self.emails[0].id
        response = self.client.post(self.get_url(), {"delete-single": email_id})
        self.assertEqual(response.status_code, 302)

        # second time around, it's already deleted but we don't want an error
        response = self.client.post(self.get_url(), {"delete-single": email_id})
        self.assertEqual(response.status_code, 302)

    def test_important_first(self):
        # mark some emails as important
        for email in self.emails[:3]:
            email.flags.important = True
            email.save()

        response = self.client.get(self.get_url())
        objs = response.context["page_obj"].object_list[:5]
        objs = [obj.important for obj in objs]

        self.assertEqual(objs, [1, 1, 1, 0, 0])

    def test_pagin(self):
        # there should be 150 emails in the test fixtures
        # and pages are paginated by 100 items
        response = self.client.get(self.get_url() + "2")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.get_url() + "3")
        self.assertEqual(response.status_code, 404)


class SingleInboxTestCase(InboxTestAbstract, test.TestCase):
    """Test Inbox specific views"""
    def setUp(self):
        super(SingleInboxTestCase, self).setUp()
        self.inbox = factories.InboxFactory(user=self.user)
        self.emails = factories.EmailFactory.create_batch(150, inbox=self.inbox)

        for email in self.emails:
            part = factories.PartListFactory(email=email)
            factories.HeaderFactory(part=part)
            factories.HeaderFactory(part=part, name="From")
            factories.HeaderFactory(part=part, name="Subject")

    def get_url(self):
        return urlresolvers.reverse("single-inbox", kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})


class UnifiedInboxTestCase(InboxTestAbstract, test.TestCase):
    """Test Unified Inbox specific views"""
    def setUp(self):
        super(UnifiedInboxTestCase, self).setUp()
        self.emails = factories.EmailFactory.create_batch(150, inbox__user=self.user)

        for email in self.emails:
            part = factories.PartListFactory(email=email)
            factories.HeaderFactory(part=part, name="From")
            factories.HeaderFactory(part=part, name="Subject")

    def get_url(self):
        return urlresolvers.reverse("unified-inbox")


class InboxAddTestCase(test.TestCase):
    """Test the add inbox page"""
    def setUp(self):
        """Create the client and grab the user"""
        super(InboxAddTestCase, self).setUp()
        self.user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        for args in itertools.product([True, False], [self.user, other_user, None]):
            factories.DomainFactory(enabled=args[0], owner=args[1])

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("inbox-add")

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
        form_data = {"domain": domain_id}
        form = inboxen_forms.InboxAddForm(MockRequest(self.user), data=form_data)
        self.assertTrue(form.is_valid())

        # invalid domain
        domain_id = models.Domain.objects.filter(enabled=False)[0].id
        form_data = {"domain": domain_id}
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


class InboxEditTestCase(test.TestCase):
    """Test the edit inbox page"""
    def setUp(self):
        """Create the client and grab the user"""
        super(InboxEditTestCase, self).setUp()
        self.user = factories.UserFactory()
        self.inbox = factories.InboxFactory(user=self.user)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("inbox-edit", kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})

    def test_inbox_form(self):
        response = self.client.get(self.get_url())
        form = response.context["form"]
        self.assertIsInstance(form, inboxen_forms.InboxEditForm)

        self.assertNotIn("inbox", form.fields)
        self.assertNotIn("domain", form.fields)
        self.assertIn("description", form.fields)

    def test_inbox_add_description(self):
        response = self.client.post(self.get_url(), {"description": "nothing at all"})
        self.assertEqual(response.status_code, 302)

        self.assertTrue(models.Inbox.objects.filter(description="nothing at all").exists())
