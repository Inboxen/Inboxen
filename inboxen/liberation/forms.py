##
#    Copyright (C) 2013-2015 Jessica Tallon & Matt Molyneaux
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
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _

from inboxen.liberation import models
from inboxen.liberation.tasks import liberate as data_liberate


class LiberationForm(forms.ModelForm):
    class Meta:
        model = models.Liberation
        fields = ["compression_type", "storage_type"]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.user = user
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        if not self.user.liberation_set.all().can_request_another():
            raise ValidationError("You cannot request another archive so soon!")
        return cleaned_data

    def save(self):
        self.instance.save()
        data_liberate.apply_async(
            kwargs={"liberation_id": self.instance.id},
            countdown=10
        )
