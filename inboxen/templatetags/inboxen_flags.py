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
from django.utils.translation import ugettext_lazy

from inboxen.utils.flags import create_render_bitfield_template_tag


register = template.Library()


FLAGS_TO_TAGS = {
    "new": {
        "title": ugettext_lazy("New messages"),
        "str": ugettext_lazy("New"),
        "class": "label-primary",
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
    },
    "pinned": {
        "title": ugettext_lazy("Inbox has been pinned"),
        "str": ugettext_lazy("Pinned"),
        "class": "label-warning",
    },
    "disabled": {
        "title": ugettext_lazy("Inbox has been disabled"),
        "str": ugettext_lazy("Disabled"),
        "class": "label-default",
        "singleton": True,
    },
}


render_flags = create_render_bitfield_template_tag(FLAGS_TO_TAGS)
register.filter("render_flags", render_flags)
