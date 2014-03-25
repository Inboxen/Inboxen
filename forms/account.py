##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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
from django.contrib import auth
from django.core import exceptions
from django.utils.translation import ugettext as _
from django.contrib import messages

from queue.delete.tasks import delete_account
from queue.liberate.tasks import liberate as data_liberate

class DeleteAccountForm(forms.Form):

    username = forms.CharField(
        label="Please type your username to confirm",
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        self.request = request
        return super(DeleteAccountForm, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cleaned_data = super(DeleteAccountForm, self).clean(*args, **kwargs)
        if cleaned_data["username"] != self.user.get_username():
            raise exceptions.ValidationError(_("The username entered does not match your username"))

        return cleaned_data

    def save(self, *args, **kwargs):
        # Dispatch task and logout
        delete_account.delay(self.user.id)
        auth.logout(self.request)
        return self.user

class LiberationForm(forms.Form):

    STORAGE_TYPES = (
        (0, _("Maildir")),
        (1, _("Mailbox .mbox")),
    )

    # Could we support zip files?
    COMPRESSION_TYPES = (
        (0, _("Tarball (gzip compressed)")),
        (1, _("Tarball (bzip2 compression)")),
        (2, _("Tarball (no compression)")),
    )

    storage_type = forms.ChoiceField(choices=STORAGE_TYPES)
    compression_type = forms.ChoiceField(choices=COMPRESSION_TYPES)

    def __init__(self, request, user, initial=None, *args, **kwargs):
        self.user = user
        self.request = request
        if not initial:
            initial = {
                "storage_type": 0,
                "compression_type": 0,
            }

        return super(LiberationForm, self).__init__(initial=initial, *args, **kwargs)

    def save(self):
        data_liberate.delay(self.user.id, options=self.cleaned_data)
        messages.success(self.request, _("Fetching all your data. This may take a while, so check back later!"))
        return self.user



