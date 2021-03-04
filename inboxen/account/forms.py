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
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.core import exceptions
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext as _
from elevate.forms import ElevateForm

from inboxen import models, validators
from inboxen.account import fields
from inboxen.account.tasks import delete_account
from inboxen.forms.mixins import PlaceHolderMixin


class DeleteAccountForm(forms.Form):
    username = forms.CharField(
        label=_("Please type your username to confirm"),
        widget=forms.TextInput(attrs={'placeholder': _('Username'), 'autocomplete': 'off'}),
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
    new_password1 = fields.PasswordCheckField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )


class PlaceHolderSudoForm(PlaceHolderMixin, ElevateForm):
    def clean_password(self):
        username = self.user.get_username()
        if auth.authenticate(username=username, password=self.data['password'], request=self.request):
            return self.data['password']
        raise forms.ValidationError(_('Incorrect password'))


class PlaceHolderUserCreationForm(PlaceHolderMixin, UserCreationForm):
    """Same as auth.forms.UserCreationForm but adds a label as the placeholder in each field"""
    password1 = fields.PasswordCheckField(label=_("Password"))

    def __init__(self, *args, **kwargs):
        super(PlaceHolderUserCreationForm, self).__init__(*args, **kwargs)
        self.fields["username"].help_text = _("Letters, numbers, and the symbols @/./+/-/_ are allowed.")
        self.fields["password1"].widget.attrs.update({"autocomplete": "off"})

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

        if not settings.PER_USER_EMAIL_QUOTA:
            del self.fields["quota_options"]

    class Meta:
        model = models.UserProfile
        fields = ["prefered_domain", "display_images", "prefer_html_email", "auto_delete", "quota_options"]
        widgets = {
            "display_images": RadioSelect()
        }


class UsernameChangeForm(PlaceHolderMixin, forms.ModelForm):
    """Change username"""
    username2 = forms.CharField(label=_("Repeat new username"))

    class Meta:
        model = get_user_model()
        fields = ["username"]
        labels = {"username": _("New username")}
        help_texts = {"username": _("Letters, numbers, and the symbols @/./+/-/_ are allowed.")}

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields["username"].widget.attrs.update({"autocomplete": "off"})
        self.fields["username2"].widget.attrs.update({"autocomplete": "off"})

    def clean(self):
        super().clean()

        # we have to do this here rather than in clean_username because we want other validators to run too
        username = self.cleaned_data.get("username")

        try:
            if get_user_model().objects.filter(username__iexact=username).exists():
                raise exceptions.ValidationError(_("A user with that username already exists."),
                                                 code='duplicate_username')
        except ValueError:
            # there's a null in the username, model field validators will take
            # care of that (they come later)
            pass

    def clean_username2(self):
        username1 = self.cleaned_data.get('username')
        username2 = self.cleaned_data.get('username2')
        if username1 and username2:
            if username1 != username2:
                raise forms.ValidationError(_("The two username fields don't match."))
        return username2
