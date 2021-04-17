##
#    Copyright (C) 2021 Jessica Tallon & Matt Molyneaux
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

from django.http import JsonResponse
from django.template import Context, Template
from django.utils.cache import patch_response_headers

from inboxen.templatetags.inboxen_flags import FLAGS_TO_TAGS

MAX_AGE = 60 * 60 * 24 * 7 * 52  # a year

SNIPPETS = {
    "pinned-flag": (
        """{% include "inboxen/includes/flag.html" with class=class str=str title=title %}""",
        FLAGS_TO_TAGS["pinned"]
    ),
    "disabled-flag": (
        """{% include "inboxen/includes/flag.html" with class=class str=str title=title %}""",
        FLAGS_TO_TAGS["disabled"],
    ),
    "important-flag": (
        """{% include "inboxen/includes/flag.html" with class=class str=str title=title %}""",
        FLAGS_TO_TAGS["important"]
    ),
    "generic-error": (
        """{% load i18n %}<div class="alert alert-warning" role="alert">{% trans "Something went wrong!" %}</div>""",
        {}
    ),
    "close-alert-button": (
        """{% load i18n %}"""
        """<button type="button" class="close" data-dismiss="alert">"""
        """<span class="fa fa-times" aria-hidden="true"></span><span class="sr-only">{% trans "Close" %}</span>"""
        """</button>""",
        {},
    ),
    "search-loading-text": (
        """{% load i18n %}{% trans "Loading results…" %}""",
        {},
    ),
    "search-timed-out": (
        """{% load i18n %}{% trans "The search timed out. Please try again." %}""",
        {},
    ),
}


def i18n(request):
    """Render HTML snippets into static files"""

    rendered_snippets = {}
    for key, value in SNIPPETS.items():
        template = Template(value[0])
        context = Context(value[1])
        rendered_snippets[key] = template.render(context).strip()

    response = JsonResponse(rendered_snippets)
    patch_response_headers(response, MAX_AGE)
    return response
