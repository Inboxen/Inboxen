##
#    Copyright (C) 2017 Jessica Tallon & Matt Molyneaux
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
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from inboxen.models import Domain, Request


class CreateDomainForm(forms.ModelForm):
    class Meta:
        model = Domain
        fields = ["domain", "owner"]


class EditDomainForm(forms.ModelForm):
    class Meta:
        model = Domain
        fields = ["enabled", "owner"]


class EditRequestForm(forms.ModelForm):
    succeeded = forms.ChoiceField(widget=forms.Select(), label=_("Grant?"), required=True, choices=((True, _("Yes")), (False, _("No"))))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(EditRequestForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(EditRequestForm, self).save(commit=False)

        instance.date_decided = timezone.now()
        instance.authorizer = self.user

        if commit:
            instance.save()

        return instance

    class Meta:
        model = Request
        fields = ["result", "succeeded"]
