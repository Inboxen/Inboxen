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

from django import template
from django.utils.translation import gettext_lazy

from inboxen.utils.flags import create_render_bool_template_tag

register = template.Library()


DOMAIN_TO_TAGS = {
    True: {
        "title": gettext_lazy("Domain enabled"),
        "str": gettext_lazy("Enabled"),
        "class": "label-primary",
    },
    False: {
        "title": gettext_lazy("Domain disabled"),
        "str": gettext_lazy("Disabled"),
        "class": "label-default",
    },
}


render_domain = create_render_bool_template_tag(DOMAIN_TO_TAGS)
register.filter("render_domain", render_domain)
