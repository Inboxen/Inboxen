##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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
from __future__ import unicode_literals

from django import template
from django.utils import safestring
from django.utils.translation import ugettext_lazy

register = template.Library()

FLAGS_TO_TAGS = {
    "new": {
        "title": ugettext_lazy("New messages"),
        "str": ugettext_lazy("New"),
        "class": "label-primary",
        "inverse": False,
    },
    "seen": {
        "title": ugettext_lazy("New message"),
        "str": ugettext_lazy("New"),
        "class": "label-primary",
        "inverse": True,
    },
    "read": {
        "title": ugettext_lazy("Unread message"),
        "str": ugettext_lazy("Unread"),
        "class": "label-info",
        "inverse": True,
    },
    "important": {
        "title": ugettext_lazy("Message has been marked as important"),
        "str": ugettext_lazy("Important"),
        "class": "label-danger",
        "inverse": False,
    },
    "pinned": {
        "title": ugettext_lazy("Inbox has been pinned"),
        "str": ugettext_lazy("Pinned"),
        "class": "label-warning",
        "inverse": False,
    },
    "disabled": {
        "title": ugettext_lazy("Inbox has been disabled"),
        "str": ugettext_lazy("Disabled"),
        "class": "label-default",
        "inverse": False,
    },
}

# alias certain flags
FLAGS_TO_TAGS["unified_has_new_messages"] = FLAGS_TO_TAGS["new"]

LABEL_STR = "<div class=\"inline-block__wrapper\"><span class=\"label {class}\" title=\"{title}\">{str}</span></div>"


@register.filter()
def render_flags(flags_obj):
    """Takes a Bitfield BitHandler from an object and outputs Bootstrap labels"""
    if getattr(flags_obj, "disabled", False):
        return safestring.mark_safe(LABEL_STR.format(**FLAGS_TO_TAGS["disabled"]))

    flags = []
    for name, value in flags_obj:
        if name not in FLAGS_TO_TAGS:
            continue
        flag = FLAGS_TO_TAGS[name]

        # flag["inverse"] is also the flag value when it is *not* displayed
        if value == flag["inverse"]:
            continue

        flags.append(LABEL_STR.format(**flag))
    if len(flags) > 0:
        flags = "".join(flags)
        return safestring.mark_safe(flags)
    else:
        return safestring.mark_safe("&nbsp;")
