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

"""
Parts of this file are taken from django-two-factor

Copyright (C) 2014 Bouke Haarsma

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from django import forms
from django.contrib import messages
from django.forms.widgets import RadioFieldRenderer
from django.utils.encoding import force_text
from django.utils.html import format_html_join
from django.utils.translation import ugettext as _

from django_otp.plugins.otp_totp.models import TOTPDevice
from two_factor import forms as two_factor

from inboxen import models
from website.forms.mixins import BootstrapFormMixin

__all__ = ["TwoFactorForm", "MethodForm"]

class TwoFactorForm(BootstrapFormMixin, forms.Form):
    token = forms.CharField(required=True, label=_("Token"), widget=forms.TextInput(attrs={'placeholder': '123456...'}))

    def __init__(self, request, initial=None, *args, **kwargs):
        super(TwoFactorForm, self).__init__(*args, **kwargs)
        self.key = key
        self.tolerance = 1
        self.t0 = 0
        self.step = 30
        self.drift = 0
        self.digits = 6
        self.request = request

    def save(self):
        return TOTPDevice.objects.create(user=self.request.user, key=self.key,
                                         tolerance=self.tolerance, t0=self.t0,
                                         step=self.step, drift=self.drift,
                                         name='default')


class RadioField(RadioFieldRenderer):
    def render(self):
        return format_html_join(
            '\n',
            '<div class="radio">{0}</div>',
            [(force_text(w), ) for w in self],
        )

class MethodForm(two_factor.MethodForm):
    def __init__(self, **kwargs):
        super(MethodForm, self).__init__(**kwargs)
        self.fields['method'].widget.renderer = RadioField
