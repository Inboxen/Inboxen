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

import datetime

from django import test
from django.core import urlresolvers

from pytz import utc

from inboxen import models
from website import forms
from website.tests import utils

class ResurrectSelectTestCase(test.TestCase):
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        super(ResurrectSelectTestCase, self).setUp()
        self.user = models.User.objects.get(id=1)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

        self.inbox = models.Inbox.objects.filter(flags=models.Inbox.flags.deleted)
        self.inbox = self.inbox.select_related("domain")[0]

    def get_url(self):
        return urlresolvers.reverse("user-resurrect")

    def get_success_url(self):
        return urlresolvers.reverse(
                    "user-resurrect",
                    kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain},
                    )

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]

        self.assertIsInstance(form, forms.ResurrectSelectForm)

    def test_post(self):
        params = {"address": "{0}@{1}".format(self.inbox.inbox, self.inbox.domain.domain)}
        response = self.client.post(self.get_url(), params)

        self.assertRedirects(response, self.get_success_url())

    def test_invalid_address(self):
        params = {"address": "not a valid address"}
        request = utils.MockRequest(self.user)
        form = forms.ResurrectSelectForm(request, data=params)

        self.assertFalse(form.is_valid())

    def test_inbox_not_deleted(self):
        self.inbox.flags.deleted = False
        self.inbox.save()

        params = {"address": "{0}@{1}".format(self.inbox.inbox, self.inbox.domain.domain)}
        request = utils.MockRequest(self.user)
        form = forms.ResurrectSelectForm(request, data=params)

        self.assertFalse(form.is_valid())

class ResurrectInboxTestCase(test.TestCase):
    fixtures = ['inboxen_testdata.json']

    def setUp(self):
        super(ResurrectInboxTestCase, self).setUp()
        self.user = models.User.objects.get(id=1)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

        self.inbox = models.Inbox.objects.filter(flags=models.Inbox.flags.deleted)
        self.inbox = self.inbox.select_related("domain")[0]

    def get_url(self):
        return urlresolvers.reverse(
                    "user-resurrect",
                    kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain},
                    )

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        params = {"tags": "testy test"}
        response = self.client.post(self.get_url(), params)

        self.assertRedirects(response, urlresolvers.reverse("user-home"))

        new_inbox = models.Inbox.objects.get(inbox=self.inbox.inbox, domain__domain=self.inbox.domain.domain)
        timesince = datetime.datetime.now(utc) - new_inbox.created

        self.assertTrue(timesince < datetime.timedelta(minutes=5))
        self.assertEqual(new_inbox.tags, "testy test")
        self.assertEqual(new_inbox.flags.deleted, False)
