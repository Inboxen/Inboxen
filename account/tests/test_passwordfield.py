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
from django.core.exceptions import ValidationError

from account import fields, validators

BAD_PASSWORD = "aaaaaaaaaaaaa"
GOOD_PASSWORD = "abcdefgh!!!!!"  # for smaller values of "good"


class PasswordFieldTestCase(test.TestCase):
    def setUp(self):
        self.field = fields.PasswordCheckField()

    def test_field(self):
        value = self.field.clean(GOOD_PASSWORD)
        self.assertEqual(GOOD_PASSWORD, value)

    def test_field_errors(self):
        try:
            self.field.clean(BAD_PASSWORD)
        except ValidationError as error:
            errors = error.messages

        self.assertEqual(len(errors), 2)

        validation_errors = [
            u'Your password has too many repeating characters, try something more random.',
            u'You password should contain at least 2 of the following: letters, numbers, spaces, punctuation.',
        ]

        self.assertItemsEqual(validation_errors, errors)

    def test_field_min(self):
        password = "a !"

        try:
            self.field.clean(password)
        except ValidationError as error:
            errors = "".join(error.messages)

        self.assertEqual(errors, "Ensure this value has at least 12 characters (it has 3).")

    def test_field_max(self):
        password = "a" * 5000

        try:
            self.field.clean(password)
        except ValidationError as error:
            errors = error.messages

        self.assertIn("Ensure this value has at most 4096 characters (it has 5000).", errors)

    def test_field_empty(self):
        password = ""

        try:
            self.field.clean(password)
        except ValidationError as error:
            errors = error.messages

        self.assertIn("This field is required.", errors)


class ValidatorTestCase(test.TestCase):
    def test_entropy(self):
        validator = validators.EntropyValidation()

        validator(GOOD_PASSWORD)

        with self.assertRaises(ValidationError):
            validator(BAD_PASSWORD)

    def test_charclass(self):
        validator = validators.CharClassValidation()

        validator(GOOD_PASSWORD)

        with self.assertRaises(ValidationError):
            validator(BAD_PASSWORD)
