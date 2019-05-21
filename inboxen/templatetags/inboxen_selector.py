##
#    Copyright (C) 2015 Jessica Tallon & Matt Molyneaux
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

import re

from django import template

register = template.Library()

SELECTOR_REGEX = re.compile(r"([:.,@|\[\]<>+])")


@register.filter()
def escape_selector(input_str, as_data=False):
    """Takes a string and escapes characters special for CSS selectors

    E.g. `me@inboxen.org` becomes `me\\@inboxen\\.org`"""
    if as_data:
        return SELECTOR_REGEX.sub(r"\\\g<0>", input_str)
    else:
        return SELECTOR_REGEX.sub(r"\\\\\g<0>", input_str)
