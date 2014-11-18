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

from django import forms

from website import validators


class PasswordCheckField(forms.CharField):
    """Field that makes sure a password is safe(ish) and not too too long"""
    default_validators = [validators.EntropyValidation(), validators.CharClassValidation()]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 4096)
        kwargs.setdefault("min_length", 12)
        kwargs.setdefault("widget", forms.PasswordInput)

        super(PasswordCheckField, self).__init__(*args, **kwargs)
