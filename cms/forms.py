from django import forms
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailusers.forms import UserCreationForm, UserEditForm


class InboxenUserCreationForm(UserCreationForm):
    email = None
    first_name = None
    last_name = None


class InboxenUserEditForm(UserEditForm):
    email = None
    first_name = None
    last_name = None
