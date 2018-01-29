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

register = template.Library()

DOMAIN_TO_TAGS = {
    True: {
        "title": ugettext_lazy("Domain enabled"),
        "str": ugettext_lazy("Enabled"),
        "class": "label-primary",
    },
    False: {
        "title": ugettext_lazy("Domain disabled"),
        "str": ugettext_lazy("Disabled"),
        "class": "label-default",
    },
}


REQUEST_TO_TAGS = {
    True: {
        "title": ugettext_lazy("Granted request"),
        "str": ugettext_lazy("Granted"),
        "class": "label-primary",
    },
    False: {
        "title": ugettext_lazy("Rejected request"),
        "str": ugettext_lazy("Rejected"),
        "class": "label-default",
    },
    None: {
        "title": ugettext_lazy("Request pending"),
        "str": ugettext_lazy("Pending"),
        "class": "label-danger",
    },
}


LABEL_STR = "<div class=\"inline-block__wrapper\"><span class=\"label {class}\" title=\"{title}\">{str}</span></div>"


@register.filter()
def render_domain(enabled):
    flag = DOMAIN_TO_TAGS[enabled]

    return safestring.mark_safe(LABEL_STR.format(**flag))


@register.filter()
def render_request(succeeded):
    flag = REQUEST_TO_TAGS[succeeded]

    return safestring.mark_safe(LABEL_STR.format(**flag))
