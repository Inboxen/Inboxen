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

from website import validators

BAD_PASSWORD = "aaaaaaaaaa"
GOOD_PASSWORD = "abcdef!!!!" # for smaller values of "good"

class PasswordFieldTestCase(test.TestCase):
    def test_entropy(self):
        validator = validators.EntropyValidation()

        good = validator(GOOD_PASSWORD)

        with self.assertRaises(ValidationError):
            bad = validator(BAD_PASSWORD)

    def test_charclass(self):
        validator = validators.CharClassValidation()

        good = validator(GOOD_PASSWORD)

        with self.assertRaises(ValidationError):
            bad = validator(BAD_PASSWORD)
