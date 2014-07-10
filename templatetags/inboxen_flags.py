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

from django import template
from django.utils import safestring
from django.utils.translation import ugettext as _

register = template.Library()

FLAGS_TO_TAGS = {
                "new": {
                    "title": _("New messages"),
                    "str": _("New"),
                    "class": "label-primary",
                    "inverse": False,
                    },
                "read": {
                    "title": _("Unread message"),
                    "str": _("Unread"),
                    "class": "label-info",
                    "inverse": True,
                    },
                "important": {
                    "title": _("Message has been marked as important"),
                    "str": _("Important"),
                    "class": "label-danger",
                    "inverse": False,
                    },
                }

# alias certain flags
FLAGS_TO_TAGS["unified_has_new_messages"] = FLAGS_TO_TAGS["new"]
FLAGS_TO_TAGS["seen"] = FLAGS_TO_TAGS["new"]

LABEL_STR = "<span class=\"label {class}\" title=\"{title}\">{str}</span>"

@register.filter()
def render_flags(flags_obj):
    """Takes a Bitfield BitHandler from an object and outputs Bootstrap labels"""
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
    else:
        flags = "&nbsp;"

    return safestring.mark_safe(flags)
