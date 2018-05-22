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
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.core import exceptions
from django.utils.translation import ugettext as _
from elevate.forms import ElevateForm
from ratelimitbackend.forms import AuthenticationForm
import six

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


class PlaceHolderSudoForm(PlaceHolderMixin, ElevateForm):
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


class SettingsForm(forms.ModelForm):
    """A form for general settings"""
    def __init__(self, request, *args, **kwargs):
        kwargs.setdefault("instance", request.user.inboxenprofile)

        super(SettingsForm, self).__init__(*args, **kwargs)

        self.fields["prefered_domain"].queryset = models.Domain.objects.available(request.user)
        self.fields["prefered_domain"].empty_label = _("(No preference)")

    class Meta:
        model = models.UserProfile
        fields = ["prefered_domain", "display_images", "prefer_html_email"]
        labels = {
            "display_images": _("Display options for HTML emails"),
            "prefer_html_email": _("Prefer HTML emails"),
        }
        help_texts = {
            "display_images": _("Warning: Images in HTML emails can be used to track if you read an email!"),
            "prefered_domain": _("Prefer a particular domain when adding a new Inbox")
        }


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

        valids = [validators.ProhibitNullCharactersValidator()]
        if six.PY3:
            valids.append(UnicodeUsernameValidator())
        else:
            valids.append(ASCIIUsernameValidator())

        for validator in valids:
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
