##
#    Copyright (C) 2013, 2014, 2015, 2016, 2017 Jessica Tallon & Matt Molyneaux
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

from cms.utils import app_reverse
from inboxen.utils.flags import create_render_bool_template_tag


register = template.Library()


LIVE_TO_TAGS = {
    True: {
        "title": ugettext_lazy("Live post"),
        "str": ugettext_lazy("Live"),
        "class": "label-primary",
    },
    False: {
        "title": ugettext_lazy("Draft post"),
        "str": ugettext_lazy("Draft"),
        "class": "label-default",
    },
}

IN_MENU_TO_TAGS = {
    True: {
        "title": ugettext_lazy("Page will appear in menu"),
        "str": ugettext_lazy("In menu"),
        "class": "label-primary",
    },
}


@register.simple_tag(takes_context=True)
def app_url(context, viewname, *args, **kwargs):
    request = context['request']

    return app_reverse(request.page, viewname, args, kwargs)


render_live = create_render_bool_template_tag(LIVE_TO_TAGS)
register.filter("render_live", render_live)


render_in_menu = create_render_bool_template_tag(IN_MENU_TO_TAGS)
register.filter("render_in_menu", render_in_menu)
