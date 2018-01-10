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
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.core import exceptions
from django.utils.translation import ugettext as _

from ratelimitbackend.forms import AuthenticationForm
from sudo.forms import SudoForm

from account import fields
from account.tasks import delete_account
from inboxen import models
from inboxen import validators
from inboxen.forms.mixins import PlaceHolderMixin

__all__ = [
    "DeleteAccountForm", "PlaceHolderAuthenticationForm", "PlaceHolderPasswordChangeForm",
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
        self.request._logout_message = _("Account deleted. Thanks for using our service.")
        auth.logout(self.request)
        return self.user


class PlaceHolderAuthenticationForm(PlaceHolderMixin, AuthenticationForm):
    """Same as auth.forms.AuthenticationForm but adds a label as the placeholder
    in each field"""

    def clean_username(self):
        username = self.cleaned_data["username"]

        validator = validators.ProhibitNullCharactersValidator()
        validator(username)

        return username


class PlaceHolderPasswordChangeForm(PlaceHolderMixin, PasswordChangeForm):
    """Same as auth.forms.PasswordChangeForm but adds a label as the placeholder in each field"""
    new_password1 = fields.PasswordCheckField(label=_("New password"))


class PlaceHolderSudoForm(PlaceHolderMixin, SudoForm):
    pass


class PlaceHolderUserCreationForm(PlaceHolderMixin, UserCreationForm):
    """Same as auth.forms.UserCreationForm but adds a label as the placeholder in each field"""
    password1 = fields.PasswordCheckField(label=_("Password"))

    def __init__(self, *args, **kwargs):
        super(PlaceHolderUserCreationForm, self).__init__(*args, **kwargs)
        self.fields["username"].help_text = _("Letters, numbers, and the symbols @/./+/-/_ are allowed.")

    def clean_username(self):
        username = self.cleaned_data["username"]

        validator = validators.ProhibitNullCharactersValidator()
        validator(username)

        if get_user_model().objects.filter(username__iexact=username).exists():
            raise exceptions.ValidationError(_("A user with that username already exists."), code='duplicate_username')

        return username


class SettingsForm(forms.Form):
    """A form for general settings"""
    IMAGE_OPTIONS = (
        (0, _("Always ask to display images")),
        (1, _("Always display images")),
        (2, _("Never display images")),
    )

    prefered_domain = forms.ModelChoiceField(
        required=False,
        queryset=models.Domain.objects.none(),
        empty_label=_("(No preference)"),
        help_text=_("Prefer a particular domain when adding a new Inbox")
    )
    images = forms.ChoiceField(
        choices=IMAGE_OPTIONS,
        widget=forms.RadioSelect,
        label=_("Display options for HTML emails"),
        help_text=_("Warning: Images in HTML emails can be used to track if you read an email!"),
    )
    prefer_html = forms.BooleanField(required=False, label=_("Prefer HTML emails"))

    def __init__(self, request, *args, **kwargs):
        self.profile = request.user.inboxenprofile

        initial = kwargs.get("initial", {})

        initial["prefer_html"] = bool(self.profile.flags.prefer_html_email)
        initial["prefered_domain"] = self.profile.prefered_domain

        if self.profile.flags.ask_images:
            initial["images"] = "0"
        elif self.profile.flags.display_images:
            initial["images"] = "1"
        else:
            initial["images"] = "2"

        kwargs.setdefault("initial", initial)

        super(SettingsForm, self).__init__(*args, **kwargs)

        self.fields["prefered_domain"].queryset = models.Domain.objects.available(request.user)

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

        self.profile.prefered_domain = self.cleaned_data["prefered_domain"]

        self.profile.save(update_fields=["flags", "prefered_domain"])


class UsernameChangeForm(PlaceHolderMixin, forms.ModelForm):
    """Change username"""
    username2 = forms.CharField(label=_("Repeat new username"))

    class Meta:
        model = get_user_model()
        fields = ["username"]
        labels = {"username": _("New username")}
        help_texts = {"username": _("Letters, numbers, and the symbols @/./+/-/_ are allowed.")}

    def clean_username(self):
        username = self.cleaned_data["username"]

        validator = validators.ProhibitNullCharactersValidator()
        validator(username)

        if get_user_model().objects.filter(username__iexact=username).exists():
            raise exceptions.ValidationError(_("A user with that username already exists."), code='duplicate_username')

        return username

    def clean_username2(self):
        username1 = self.cleaned_data.get('username')
        username2 = self.cleaned_data.get('username2')
        if username1 and username2:
            if username1 != username2:
                raise forms.ValidationError(_("The two username fields don't match."))
        return username2
