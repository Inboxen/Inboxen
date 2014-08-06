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

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class ComplexityValidation(object):
    """Guess the complexity of a string"""
    def __call__(self, value):
        if len(set(value)) < self.min_complex:
            raise ValidationError(_("Your password is not complex enough"))

class CharClassValidation(object):
    """Checks a string contains a certain number of character classes

    regex_classes expects to be compiled regex
    """
    regex_classes = [
                re.compile(r"(?=(\w))(?=\D)", re.UNICODE),
                re.compile(r"\d", re.UNICODE),
                re.compile(r"\s", re.UNICODE),
                re.compile(r"(?=(\W))(?=\S)", re.UNICODE),
                ]
    min_classes = 2
    def __call__(self, value):
        found = 0
        for regex in self.regex_classes:
            if len(regex.findall(value)) > 0:
                found = found + 1

        if found < self.min_classes:
            raise ValidationError(_("You password doens't contain enough different character classes"))
