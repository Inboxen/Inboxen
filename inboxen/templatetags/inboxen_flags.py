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
from django.utils.translation import gettext_lazy

from inboxen.utils.flags import create_render_bitfield_template_tag

register = template.Library()


FLAGS_TO_TAGS = {
    "new": {
        "title": gettext_lazy("New messages"),
        "str": gettext_lazy("New"),
        "class": "label-primary",
    },
    "seen": {
        "title": gettext_lazy("New message"),
        "str": gettext_lazy("New"),
        "class": "label-primary",
        "inverse": True,
    },
    "read": {
        "title": gettext_lazy("Unread message"),
        "str": gettext_lazy("Unread"),
        "class": "label-info",
        "inverse": True,
    },
    "important": {
        "title": gettext_lazy("Message has been marked as important"),
        "str": gettext_lazy("Important"),
        "class": "label-danger",
    },
    "pinned": {
        "title": gettext_lazy("Inbox has been pinned"),
        "str": gettext_lazy("Pinned"),
        "class": "label-warning",
    },
    "disabled": {
        "title": gettext_lazy("Inbox has been disabled"),
        "str": gettext_lazy("Disabled"),
        "class": "label-default",
        "singleton": True,
    },
}


render_flags = create_render_bitfield_template_tag(FLAGS_TO_TAGS)
register.filter("render_flags", render_flags)
