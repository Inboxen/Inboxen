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
from __future__ import unicode_literals

import itertools

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core import urlresolvers
import six

from account.forms import SettingsForm, UsernameChangeForm, DeleteAccountForm
from inboxen.tests import factories
from inboxen.test import MockRequest, InboxenTestCase, grant_sudo


class SettingsTestCase(InboxenTestCase):
    def setUp(self):
        super(SettingsTestCase, self).setUp()
        self.user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        for args in itertools.product([True, False], [self.user, other_user, None]):
            factories.DomainFactory(enabled=args[0], owner=args[1])

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("user-settings")

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, SettingsForm)

        for domain in form.fields["prefered_domain"].queryset:
            self.assertTrue(domain.enabled)
            self.assertTrue(domain.owner is None or domain.owner.id == self.user.id)

    def test_form_bad_data(self):
        params = {"images": "12213"}
        request = MockRequest(self.user)
        form = SettingsForm(request, data=params)

        self.assertFalse(form.is_valid())

    def test_form_good_data(self):
        request = MockRequest(self.user)

        params = {"images": "1"}
        form = SettingsForm(request, data=params)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertFalse(form.profile.flags.ask_images)
        self.assertTrue(form.profile.flags.display_images)
        self.assertFalse(form.profile.flags.prefer_html_email)

        params = {"images": "2"}
        form = SettingsForm(request, data=params)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertFalse(form.profile.flags.ask_images)
        self.assertFalse(form.profile.flags.display_images)
        self.assertFalse(form.profile.flags.prefer_html_email)

        params = {"images": "0"}
        form = SettingsForm(request, data=params)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(form.profile.flags.ask_images)
        self.assertFalse(form.profile.flags.prefer_html_email)

        params = {"prefer_html": "on", "images": "0"}
        form = SettingsForm(request, data=params)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(form.profile.flags.prefer_html_email)

    def test_form_domains_valid(self):
        request = MockRequest(self.user)
        form = SettingsForm(request)

        for domain in form.fields["prefered_domain"].queryset:
            if domain.owner != self.user and domain.owner is not None:
                self.fail("Domain shouldn't be available")


class UsernameChangeTestCase(InboxenTestCase):
    def setUp(self):
        super(UsernameChangeTestCase, self).setUp()
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("user-username")

    def test_form_bad_data(self):
        params = {"username": self.user.username, "username2": self.user.username}
        form = UsernameChangeForm(data=params)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], [u"A user with that username already exists."])

        params = {"username": self.user.username + "1", "username2": self.user.username}
        form = UsernameChangeForm(data=params)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username2"], [u"The two username fields don't match."])

        params = {"username": "username\x00", "username2": "username\x00"}
        form = UsernameChangeForm(data=params)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], [u"Null characters are not allowed."])

        params = {"username": "username€", "username2": "username€"}
        form = UsernameChangeForm(data=params)
        self.assertFalse(form.is_valid())
        if six.PY3:
            expected_errors = [u"Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."]  # noqa: E501
        else:
            expected_errors = [u"Enter a valid username. This value may contain only English letters, numbers, and @/./+/-/_ characters."]  # noqa: E501
        self.assertEqual(form.errors["username"], expected_errors)

    def test_form_good_data(self):
        username = self.user.username

        params = {"username": self.user.username + "1", "username2": self.user.username + "1"}
        form = UsernameChangeForm(data=params)

        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        new_user = get_user_model().objects.get(pk=form.instance.pk)
        self.assertEqual(new_user.username, username + "1")

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "{}?next={}".format(urlresolvers.reverse("user-sudo"), self.get_url()))

        grant_sudo(self.client)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        grant_sudo(self.client)
        other_user = factories.UserFactory(username=self.user.username + "2")
        new_username = self.user.username + "1"
        old_username = self.user.username
        other_username = other_user.username
        user_count = get_user_model().objects.count()

        # invalid form
        params = {"username": new_username, "username2": old_username}
        response = self.client.post(self.get_url(), params)
        self.user.refresh_from_db()
        other_user.refresh_from_db()

        # username should remain unchanged
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.username, old_username)
        self.assertEqual(other_user.username, other_username)
        self.assertEqual(get_user_model().objects.count(), user_count)

        # valid form
        params = {"username": new_username, "username2": new_username}
        response = self.client.post(self.get_url(), params)
        self.user.refresh_from_db()
        other_user.refresh_from_db()

        # username should changed
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], urlresolvers.reverse("user-settings"))
        self.assertEqual(self.user.username, new_username)
        self.assertEqual(other_user.username, other_username)
        self.assertEqual(get_user_model().objects.count(), user_count)


class DeleteTestCase(InboxenTestCase):
    def setUp(self):
        super(DeleteTestCase, self).setUp()
        self.user = factories.UserFactory()

        login = self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("user-delete")

    def test_form_good_data(self):
        params = {"username": self.user.username}
        request = MockRequest(self.user)
        form = DeleteAccountForm(request, data=params)

        self.assertTrue(form.is_valid())

        form.save()

        self.assertEqual(request.user, AnonymousUser())
        messages = list(request._messages)
        self.assertEqual(str(messages[0]), "Account deleted. Thanks for using our service.")

    def test_form_bad_data(self):
        params = {"username": "derp" + self.user.username}
        request = MockRequest(self.user)
        form = DeleteAccountForm(request, data=params)

        self.assertFalse(form.is_valid())

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "{}?next={}".format(urlresolvers.reverse("user-sudo"), self.get_url()))

        grant_sudo(self.client)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
