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
from django.core import urlresolvers


class SettingsMenuNode(template.Node):
    """Render the menu on a settings page, highlighting the current item"""
    container_class = "nav nav-pills"
    container_tag = "ul"
    item_active_class = "active"
    item_default_class = ""
    item_tag = "li"
    item_template = "<{tag} class=\"{classes}\"><a href=\"{url}\">{title}</a></{tag}>"

    # tuple of (url_name, title)
    menu = (
        ("user-settings", _("General")),
        ("user-liberate", _("Liberate Data")),
        ("user-security", _("Security")),
        ("user-delete", _("Delete Account")),
        )

    def __init__(self, url_name):
        self.container = "<{tag} class=\"{classes}\">%s</{tag}>".format(
                                tag=self.container_tag,
                                classes=self.container_class
                                )
        self.active = url_name

    def render(self, context):
        items = []

        for url, title in self.menu:
            classes = self.item_default_class
            if url == self.active:
                classes = classes + self.item_active_class

            url = urlresolvers.reverse(url)

            menu_item = self.item_template.format(tag=self.item_tag, classes=classes, url=url, title=title)
            items.append(menu_item)

        output = "".join(items)
        output = self.container % output
        return output


register = template.Library()

@register.tag
def settings_menu(parser, token):
    try:
        tag_name, url_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

    if not (url_name[0] == url_name[-1] and url_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)

    url_name = url_name[1:-1].strip()
    return SettingsMenuNode(url_name)
