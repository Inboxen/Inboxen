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

from inboxen.account import forms
from inboxen.test import InboxenTestCase, MockRequest
from inboxen.tests import factories


class LowerCaseUsernameTestCase(InboxenTestCase):
    def setUp(self):
        self.user = factories.UserFactory(username="isdabizda")

    def test_login(self):
        params = {"username": "ISdaBIZda", "password": "123456"}
        form = forms.PlaceHolderAuthenticationForm(data=params, request=MockRequest(self.user))

        self.assertTrue(form.is_valid())

    def test_login_fail(self):
        params = {"username": "hiii", "password": "123456"}
        form = forms.PlaceHolderAuthenticationForm(data=params, request=MockRequest(self.user))

        self.assertFalse(form.is_valid())

        params = {"username": "isdabizda", "password": "1234567"}
        form = forms.PlaceHolderAuthenticationForm(data=params, request=MockRequest(self.user))

        self.assertFalse(form.is_valid())

    def test_create_fail(self):
        params = {"username": "ISdaBIZda", "password1": "123456qwerty", "password2": "123456qwerty"}
        form = forms.PlaceHolderUserCreationForm(data=params)

        self.assertFalse(form.is_valid())

    def test_create_pass(self):
        params = {"username": "hewwo", "password1": "123456qwerty", "password2": "123456qwerty"}
        form = forms.PlaceHolderUserCreationForm(data=params)

        self.assertTrue(form.is_valid())

    def test_change_fail_case_insensitive(self):
        params = {"username": "ISDABIZDA", "username2": "ISDABIZDA"}
        form = forms.UsernameChangeForm(data=params)

        self.assertFalse(form.is_valid())

    def test_change_pass(self):
        params = {"username": "hello1", "username2": "hello1"}
        form = forms.UsernameChangeForm(data=params)

        self.assertTrue(form.is_valid())
