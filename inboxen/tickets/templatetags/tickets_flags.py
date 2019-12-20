##
#    Copyright (C) 2016, 2018 Jessica Tallon & Matt Molyneaux
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

from inboxen.tickets.models import Question
from inboxen.utils.flags import create_render_bool_template_tag

register = template.Library()


STATUS = {k: v for k, v in Question.STATUS_CHOICES}


STATUS_TO_TAGS = {
    Question.NEW: {
        "title": gettext_lazy("New question"),
        "str": STATUS[Question.NEW],
        "class": "label-primary",
    },
    Question.IN_PROGRESS: {
        "title": gettext_lazy("In progress"),
        "str": STATUS[Question.IN_PROGRESS],
        "class": "label-info",
    },
    Question.NEED_INFO: {
        "title": gettext_lazy("Need more info from user"),
        "str": STATUS[Question.NEED_INFO],
        "class": "label-warning",
    },
    Question.RESOLVED: {
        "title": gettext_lazy("Resolved question"),
        "str": STATUS[Question.RESOLVED],
        "class": "label-default",
    },
}


render_status = create_render_bool_template_tag(STATUS_TO_TAGS)
register.filter("render_status", render_status)
