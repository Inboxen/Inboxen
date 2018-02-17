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

from datetime import timedelta

from bitfield import BitHandler
from django import forms
from django.contrib.messages.constants import DEFAULT_LEVELS
from django.contrib.messages.utils import get_level_tags
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
import mock

from inboxen.forms.inbox import InboxEditForm


class Form(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Placeholder'}))
    checkbox = forms.BooleanField()
    dropdown = forms.ChoiceField(choices=((0, "Thing"), (1, "Other thing")))
    radio = forms.ChoiceField(widget=forms.RadioSelect, choices=((0, "Thing"), (1, "Other thing")))


@require_GET
def styleguide(request):
    now = timezone.now() + timedelta(-1)
    domain = mock.Mock(domain="example.com")

    # create a bunch of mocked inboxes
    inboxes = [
        mock.Mock(
            inbox="qwerty",
            domain=domain,
            flags=BitHandler(0, ["new"]),
            last_activity=now,
            form=InboxEditForm(request),
        ),
        mock.Mock(
            inbox="qwerty",
            domain=domain,
            flags=BitHandler(1, ["disabled"]),
            last_activity=now,
            form=False,
        ),
        mock.Mock(inbox="qwerty",
            domain=domain,
            flags=BitHandler(1 | 2, ["new", "pinned"]),
            last_activity=now,
            form=False,
        ),
    ]

    # emails
    emails = [
         mock.Mock(
            inbox=inboxes[0],
            flags=BitHandler(1, ["important"]),
            received_date=now,
        ),
        mock.Mock(
            inbox=inboxes[0],
            flags=BitHandler(0, ["important"]),
            received_date=now,
        ),
    ]


    # attachments
    attachments = [
        mock.Mock(id=0, filename=("a" * 100), content_type="blah/blah", get_children=[]),
        mock.Mock(id=0, filename="a", content_type=None, get_children=[]),
    ]

    context = {
        "inboxes": inboxes,
        "emails": emails,
        "attachments": attachments,
        "form": Form(),
        "message_types": [(k, get_level_tags()[v]) for k, v in DEFAULT_LEVELS.items() if k != 'DEBUG'],
    }
    return TemplateResponse(request, 'inboxen/styleguide.html', context)
