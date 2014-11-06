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

from datetime import datetime

from django import forms
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.core import exceptions
from django.utils.translation import ugettext as _

from ratelimitbackend.forms import AuthenticationForm
from pytz import utc

from inboxen import models
from queue.delete.tasks import delete_account
from queue.liberate.tasks import liberate as data_liberate
from website import fields
from website.forms.mixins import PlaceHolderMixin

__all__ = [
    "DeleteAccountForm", "LiberationForm",
    "PlaceHolderAuthenticationForm", "PlaceHolderPasswordChangeForm",
    "PlaceHolderUserCreationForm", "SettingsForm", "UsernameChangeForm",
]


class DeleteAccountForm(forms.Form):

    username = forms.CharField(
        label=_("Please type your username to confirm"),
        widget=forms.TextInput(attrs={'placeholder': _('Username')}),
        required=False,
    )

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        self.request = request
        return super(DeleteAccountForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(DeleteAccountForm, self).clean()
        if cleaned_data.get("username", "") != self.user.get_username():
            raise exceptions.ValidationError(_("The username entered does not match your username"))

        return cleaned_data

    def save(self):
        # Dispatch task and logout
        delete_account.delay(self.user.id)
        auth.logout(self.request)
        return self.user


class LiberationForm(forms.ModelForm):
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
        lib_status = self.user.liberation
        if not lib_status.flags.running:
            lib_status.flags = models.Liberation.flags.running
            lib_status.started = datetime.now(utc)

            result = data_liberate.apply_async(
                kwargs={"user_id": self.user.id, "options": self.cleaned_data},
                countdown=10
            )

            lib_status.async_result = result.id
            lib_status.save()

        return self.user


class PlaceHolderAuthenticationForm(PlaceHolderMixin, AuthenticationForm):
    """Same as auth.forms.AuthenticationForm but adds a label as the placeholder
    in each field"""
    pass


class PlaceHolderPasswordChangeForm(PlaceHolderMixin, PasswordChangeForm):
    """Same as auth.forms.PasswordChangeForm but adds a label as the placeholder in each field"""
    new_password1 = fields.PasswordCheckField(label=_("New password"))


class PlaceHolderUserCreationForm(PlaceHolderMixin, UserCreationForm):
    """Same as auth.forms.UserCreationForm but adds a label as the placeholder in each field"""
    password1 = fields.PasswordCheckField(label=_("Password"))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if get_user_model().objects.filter(username__iexact=username).exists():
            raise exceptions.ValidationError(
                self.error_messages['duplicate_username'],
                code='duplicate_username',
                )
        return username


class SettingsForm(PlaceHolderMixin, forms.Form):
    """A form for general settings"""
    IMAGE_OPTIONS = (
        (0, _("Always ask to display images")),
        (1, _("Always display images")),
        (2, _("Never display images")),
        )
    images = forms.ChoiceField(choices=IMAGE_OPTIONS, widget=forms.RadioSelect, label=_("Display options for HTML emails"))
    prefer_html = forms.BooleanField(required=False, label=_("Prefer HTML emails"))

    def __init__(self, request, *args, **kwargs):
        self.profile = request.user.userprofile

        initial = kwargs.get("initial", {})

        initial["prefer_html"] = bool(self.profile.flags.prefer_html_email)

        if self.profile.flags.ask_images:
            initial["images"] = "0"
        elif self.profile.flags.display_images:
            initial["images"] = "1"
        else:
            initial["images"] = "2"

        kwargs.setdefault("initial", initial)
        super(SettingsForm, self).__init__(*args, **kwargs)

    def save(self):
        if "prefer_html" in self.cleaned_data and self.cleaned_data["prefer_html"]:
            self.profile.flags.prefer_html_email = True
        else:
            self.profile.flags.prefer_html_email = False

        if "images" in self.cleaned_data:
            if self.cleaned_data["images"] == "0":
                self.profile.flags.ask_images = True
            elif self.cleaned_data["images"] == "1":
                self.profile.flags.display_images = True
                self.profile.flags.ask_images = False
            elif self.cleaned_data["images"] == "2":
                self.profile.flags.display_images = False
                self.profile.flags.ask_images = False

        self.profile.save(update_fields=["flags"])


class UsernameChangeForm(PlaceHolderMixin, forms.Form):
    """Change username"""
    new_username1 = forms.CharField(label=_("New username"))
    new_username2 = forms.CharField(label=_("Repeat new username"))

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        super(UsernameChangeForm, self).__init__(*args, **kwargs)

    def clean_new_username1(self):
        username = self.cleaned_data.get('new_username1')
        if get_user_model().objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_("This username is already taken"))

        return username

    def clean_new_username2(self):
        username1 = self.cleaned_data.get('new_username1')
        username2 = self.cleaned_data.get('new_username2')
        if username1 and username2:
            if username1 != username2:
                raise forms.ValidationError(_("The two username fields don't match."))
        return username2

    def save(self):
        username = self.cleaned_data["new_username1"]
        self.user.username = username
        self.user.save(update_fields=["username"])
