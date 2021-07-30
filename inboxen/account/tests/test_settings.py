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

import itertools

from django import urls
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from inboxen.account.forms import DeleteAccountForm, PlaceHolderPasswordChangeForm, SettingsForm, UsernameChangeForm
from inboxen.test import InboxenTestCase, MockRequest, grant_sudo
from inboxen.tests import factories


class SettingsTestCase(InboxenTestCase):
    def setUp(self):
        super(SettingsTestCase, self).setUp()
        self.user = factories.UserFactory()
        other_user = factories.UserFactory(username="lalna")

        for args in itertools.product([True, False], [self.user, other_user, None]):
            factories.DomainFactory(enabled=args[0], owner=args[1])

        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

    def get_url(self):
        return urls.reverse("user-settings")

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, SettingsForm)

        for domain in form.fields["prefered_domain"].queryset:
            self.assertTrue(domain.enabled)
            self.assertTrue(domain.owner is None or domain.owner.id == self.user.id)

    def test_form_bad_data(self):
        params = {"display_images": "12213"}
        request = MockRequest(self.user)
        form = SettingsForm(request, data=params)

        self.assertFalse(form.is_valid())

    def test_form_good_data(self):
        request = MockRequest(self.user)

        params = {"display_images": "1"}
        form = SettingsForm(request, data=params)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.user.inboxenprofile.refresh_from_db()
        self.assertEqual(self.user.inboxenprofile.display_images, 1)
        self.assertFalse(self.user.inboxenprofile.prefer_html_email)

        params = {"display_images": "2"}
        form = SettingsForm(request, data=params)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.user.inboxenprofile.refresh_from_db()
        self.assertEqual(self.user.inboxenprofile.display_images, 2)
        self.assertFalse(self.user.inboxenprofile.prefer_html_email)

        params = {"display_images": "0"}
        form = SettingsForm(request, data=params)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.user.inboxenprofile.refresh_from_db()
        self.assertEqual(self.user.inboxenprofile.display_images, 0)
        self.assertFalse(self.user.inboxenprofile.prefer_html_email)

        params = {"prefer_html_email": "on", "display_images": "0"}
        form = SettingsForm(request, data=params)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(self.user.inboxenprofile.display_images, 0)
        self.assertTrue(self.user.inboxenprofile.prefer_html_email)

    def test_form_domains_valid(self):
        request = MockRequest(self.user)
        form = SettingsForm(request)

        for domain in form.fields["prefered_domain"].queryset:
            self.assertTrue(domain.owner == self.user or domain.owner is None)


class UsernameChangeTestCase(InboxenTestCase):
    def setUp(self):
        super(UsernameChangeTestCase, self).setUp()
        self.user = factories.UserFactory()

        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

    def get_url(self):
        return urls.reverse("user-username")

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
        expected_errors = [u"Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."]  # noqa: E501
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
        self.assertEqual(response["Location"], "{}?next={}".format(urls.reverse("user-sudo"), self.get_url()))

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
        self.assertEqual(response["Location"], urls.reverse("user-settings"))
        self.assertEqual(self.user.username, new_username)
        self.assertEqual(other_user.username, other_username)
        self.assertEqual(get_user_model().objects.count(), user_count)


class DeleteTestCase(InboxenTestCase):
    def setUp(self):
        super(DeleteTestCase, self).setUp()
        self.user = factories.UserFactory()

        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

    def get_url(self):
        return urls.reverse("user-delete")

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
        self.assertEqual(response["Location"], "{}?next={}".format(urls.reverse("user-sudo"), self.get_url()))

        grant_sudo(self.client)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)


class PasswordChangeTestCase(InboxenTestCase):
    def setUp(self):
        super().setUp()
        self.user = factories.UserFactory()

        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

    def get_url(self):
        return urls.reverse("user-password")

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context["form"], PlaceHolderPasswordChangeForm))

    def test_post(self):
        old_password_hash = self.user.password
        params = {
            "old_password": "123456",
            "new_password1": "qwerty123456",
            "new_password2": "qwerty123456",
        }
        response = self.client.post(self.get_url(), params)
        self.user.refresh_from_db()

        self.assertRedirects(response, urls.reverse("user-settings"), fetch_redirect_response=False)
        self.assertNotEqual(self.user.password, old_password_hash)

    def test_post_bad(self):
        old_password_hash = self.user.password
        params = {
            "old_password": "123456",
            "new_password1": "qwerty",
            "new_password2": "qwerty123456",
        }
        response = self.client.post(self.get_url(), params)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.password, old_password_hash)


class SudoTestCase(InboxenTestCase):
    def setUp(self):
        super().setUp()
        self.user = factories.UserFactory()

        assert self.client.login(username=self.user.username, password="123456", request=MockRequest(self.user))

        self.sudo_protected_url = urls.reverse("user-delete")
        self.sudo_url = urls.reverse("user-sudo")

    def test_good_password(self):
        response = self.client.get(self.sudo_protected_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "{}?next={}".format(self.sudo_url, self.sudo_protected_url))

        response = self.client.post(response["Location"], {"password": "123456"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.sudo_protected_url)

        response = self.client.get(self.sudo_protected_url)
        self.assertEqual(response.status_code, 200)

    def test_bad_password(self):
        response = self.client.get(self.sudo_protected_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "{}?next={}".format(self.sudo_url, self.sudo_protected_url))

        response = self.client.post(response["Location"], {"password": "qwerty"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].is_valid(), False)

        response = self.client.get(self.sudo_protected_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "{}?next={}".format(self.sudo_url, self.sudo_protected_url))
