##
#    Copyright (C) 2017 Jessica Tallon, Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from django import forms
from django.views.decorators.http import require_GET
from django.template.response import TemplateResponse
from django.contrib.messages.utils import get_level_tags
from django.contrib.messages.constants import DEFAULT_LEVELS


class Form(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Placeholder'}))
    checkbox = forms.BooleanField()
    dropdown = forms.ChoiceField(choices=((0, "Thing"), (1, "Other thing")))
    radio = forms.ChoiceField(widget=forms.RadioSelect, choices=((0, "Thing"), (1, "Other thing")))


@require_GET
def styleguide(request):
    context = {
        "form": Form(),
        "message_types": [(k, get_level_tags()[v]) for k, v in DEFAULT_LEVELS.items() if k != 'DEBUG'],
    }
    return TemplateResponse(request, 'inboxen/styleguide.html', context)
