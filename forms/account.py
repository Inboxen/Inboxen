##
#    Copyright (C) 2013-2014 Jessica Tallon & Matt Molyneaux
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
from django.contrib.auth.forms import PasswordChangeForm
from django.core import exceptions
from django.utils.translation import ugettext as _

from ratelimitbackend.forms import AuthenticationForm

from inboxen import models
from queue.delete.tasks import delete_account
from queue.liberate.tasks import liberate as data_liberate
from website.forms.mixins import BootstrapFormMixin, PlaceHolderMixin

class DeleteAccountForm(BootstrapFormMixin, forms.Form):

    username = forms.CharField(
        label=_("Please type your username to confirm"),
        widget=forms.TextInput(attrs={'placeholder': _('Username')})
    )

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        self.request = request
        return super(DeleteAccountForm, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cleaned_data = super(DeleteAccountForm, self).clean(*args, **kwargs)
        if cleaned_data.get("username", "") != self.user.get_username():
            raise exceptions.ValidationError(_("The username entered does not match your username"))

        return cleaned_data

    def save(self, *args, **kwargs):
        # Dispatch task and logout
        delete_account.delay(self.user.id)
        auth.logout(self.request)
        return self.user

class LiberationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = models.Inbox
        fields = []

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

    def __init__(self, user, initial=None, *args, **kwargs):
        self.user = user
        if not initial:
            initial = {
                "storage_type": 0,
                "compression_type": 0,
            }

        return super(LiberationForm, self).__init__(initial=initial, *args, **kwargs)

    def save(self):
        data_liberate.delay(self.user.id, options=self.cleaned_data)
        return self.user

class PlaceHolderAuthenticationForm(BootstrapFormMixin, PlaceHolderMixin, AuthenticationForm):
    """Same as auth.forms.AuthenticationForm but adds a label as the placeholder in each field"""
    pass

class PlaceHolderPasswordChangeForm(BootstrapFormMixin, PlaceHolderMixin, PasswordChangeForm):
    """Same as auth.forms.PasswordChangeForm but adds a label as the placeholder in each field"""
    pass
