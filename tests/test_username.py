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
from django.contrib.auth import get_user_model
from django.core import urlresolvers
from django.utils import unittest

from inboxen import models
from website import forms

@unittest.skip("Username checking is still case sensitive")
class LowerCaseUsernameTestCase(test.TestCase):
    fixtures = ['inboxen_testdata.json']

    def test_login(self):
        params = {"username": "ISdaBIZZda", "password": "123456"}
        form = forms.PlaceHolderAuthenticationForm(data=params)

        self.assertTrue(form.is_valid())

    def test_create(self):
        params = {"username": "ISdaBIZZda", "password1": "123456qwerty", "password2": "123456qwerty"}
        form = forms.PlaceHolderUserCreationForm(data=params)

        self.assertFalse(form.is_valid())

    def test_change(self):
        raise NotImplementedError("The settings view is still function based and doesn't use forms either")
