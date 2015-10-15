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

import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

__all__ = ["EntropyValidation", "CharClassValidation"]


class EntropyValidation(object):
    """Guess the entropy of a string"""
    min_entropy = 0.5
    message = _("Your password has too many repeating characters, try something more random.")

    def __call__(self, value):
        entropy = len(set(value))/float(len(value))
        if entropy < self.min_entropy:
            raise ValidationError(self.message)


class CharClassValidation(object):
    """Checks a string contains a certain number of character classes

    regex_classes expects to be compiled regex
    """
    regex_classes = [
        re.compile(r"(?=(\w))(?=\D)", re.UNICODE),  # letters
        re.compile(r"\d", re.UNICODE),              # numbers
        re.compile(r"\s", re.UNICODE),              # whitespace
        re.compile(r"(?=(\W))(?=\S)", re.UNICODE),  # punctuation
    ]
    min_classes = 2
    message = _("You password should contain at least {0} of the following: letters, numbers, spaces, punctuation.")

    def __call__(self, value):
        found = 0
        for regex in self.regex_classes:
            if len(regex.findall(value)) > 0:
                found = found + 1

        if found < self.min_classes:
            raise ValidationError(self.message.format(self.min_classes))
