##
#    Copyright (C) 2016 Jessica Tallon & Matt Molyneaux
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
from django.utils.translation import ugettext as _

from tickets.models import Question

register = template.Library()

LABEL_STR = "<div class=\"inline-block__wrapper\"><span class=\"label {class}\" title=\"{str}\">{str}</span></div>"

STATUSES = {k: v for k, v in Question.STATUS_CHOICES}

STATUS_TO_TAGS = {
    Question.NEW: {
        "str": STATUSES[Question.NEW],
        "class": "label-primary",
    },
    Question.IN_PROGRESS: {
        "str": STATUSES[Question.IN_PROGRESS],
        "class": "label-info",
    },
    Question.NEED_INFO: {
        "str": STATUSES[Question.NEED_INFO],
        "class": "label-danger",
    },
    Question.RESOLVED: {
        "str": STATUSES[Question.RESOLVED],
        "class": "label-default",
    },
}


@register.filter()
def render_status(status):
    return safestring.mark_safe(LABEL_STR.format(**STATUS_TO_TAGS[status]))
