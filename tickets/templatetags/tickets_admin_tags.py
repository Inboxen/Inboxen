##
#    Copyright (C) 2018 Jessica Tallon & Matt Molyneaux
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

from tickets.models import Question

register = template.Library()

STATUS_TO_TAGS = {
    Question.NEW: {
        "title": ugettext_lazy("New question"),
        "str": ugettext_lazy("New"),
        "class": "label-primary",
    },
    Question.IN_PROGRESS: {
        "title": ugettext_lazy("In progress"),
        "str": ugettext_lazy("In progress"),
        "class": "label-info",
    },
    Question.NEED_INFO: {
        "title": ugettext_lazy("Need more info from user"),
        "str": ugettext_lazy("Needs info"),
        "class": "label-warning",
    },
    Question.RESOLVED: {
        "title": ugettext_lazy("Resolved question"),
        "str": ugettext_lazy("Resolved"),
        "class": "label-default",
    },
}


LABEL_STR = "<div class=\"inline-block__wrapper\"><span class=\"label {class}\" title=\"{title}\">{str}</span></div>"


@register.filter()
def render_status(status):
    flag = STATUS_TO_TAGS[status]

    return safestring.mark_safe(LABEL_STR.format(**flag))
