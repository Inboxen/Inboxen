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
from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.core import urlresolvers

from inboxen import models
from website import forms
from website.tests import utils

class SettingsTestCase(test.TestCase):
    fixtures = ['inboxen_testdata.json']
    form = forms.SettingsForm

    def setUp(self):
        super(SettingsTestCase, self).setUp()
        self.user = get_user_model().objects.get(id=1)

        login = self.client.login(username=self.user.username, password="123456")

        if not login:
            raise Exception("Could not log in")

    def get_url(self):
        return urlresolvers.reverse("user-settings")

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, self.form)

    def test_form_bad_data(self):
        params = {"images": "12213"}
        request = utils.MockRequest(self.user)
        form = self.form(request, data=params)

        self.assertFalse(form.is_valid())

    def test_form_good_data(self):
        params = {"images": "1"}
        request = utils.MockRequest(self.user)
        form = self.form(request, data=params)

        self.assertTrue(form.is_valid())

class UsernameChangeTestCase(SettingsTestCase):
    form = forms.UsernameChangeForm

    def get_url(self):
        return urlresolvers.reverse("user-username")

    def test_form_bad_data(self):
        params = {"new_username1": self.user.username, "new_username2": self.user.username}
        request = utils.MockRequest(self.user)
        form = self.form(request, data=params)

        self.assertFalse(form.is_valid())

    def test_form_good_data(self):
        params = {"new_username1": self.user.username + "1", "new_username2": self.user.username + "1"}
        request = utils.MockRequest(self.user)
        form = self.form(request, data=params)

        self.assertTrue(form.is_valid())

class LiberateTestCase(SettingsTestCase):
    form = forms.LiberationForm

    def get_url(self):
        return urlresolvers.reverse("user-liberate")

    def test_form_bad_data(self):
        params = {"storage_type": 180, "compression_type": 180}
        form = self.form(user=self.user, data=params)

        self.assertFalse(form.is_valid())

    def test_form_good_data(self):
        params = {"storage_type": 1, "compression_type": 1}
        form = self.form(user=self.user, data=params)

        self.assertTrue(form.is_valid())

class DeleteTestCase(SettingsTestCase):
    form = forms.DeleteAccountForm

    def get_url(self):
        return urlresolvers.reverse("user-delete")

    def test_form_good_data(self):
        params = {"username": self.user.username}
        request = utils.MockRequest(self.user)
        form = self.form(request, data=params)

        self.assertTrue(form.is_valid())

    def test_form_bad_data(self):
        params = {"username": "derp" + self.user.username}
        request = utils.MockRequest(self.user)
        form = self.form(request, data=params)

        self.assertFalse(form.is_valid())
