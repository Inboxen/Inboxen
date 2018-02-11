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

from django.template import loader
from django.utils import safestring

from inboxen.context_processors import reduced_settings_context


def create_render_bool_template_tag(flags, template_path="inboxen/flags/bool.html"):
    template = loader.get_template(template_path)

    def render_bool(value):
        """Takes a value from a BooleanField or NullBooleanField and outputs a
        single Bootstrap label"""
        try:
            context = flags[value]
        except KeyError:
            return safestring.mark_safe("&nbsp;")
        return template.render(context)

    return render_bool


def create_render_bitfield_template_tag(flags, template_path="inboxen/flags/bitfield.html"):
    template = loader.get_template(template_path)

    def render_bitfield(flags_obj):
        """Takes a Bitfield BitHandler from an object and outputs Bootstrap
        labels"""
        flags_to_render = []
        for name, value in flags_obj:
            if name not in flags:
                continue
            flag = flags[name]

            if flag.get("singleton", False) and value is True:
                # some tags need to be displayed alone, e.g. a disabled inbox
                flags_to_render = [flag]
                break

            # flag["inverse"] is also the flag value when it is *not* displayed
            if value == flag.get("inverse", False):
                continue

            flags_to_render.append(flag)

        context = {"flags": flags_to_render}
        return template.render(context)

    return render_bitfield
