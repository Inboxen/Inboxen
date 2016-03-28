##
#    Copyright (C) 2013-2015 Jessica Tallon, Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

import logging

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from inboxen.views import base


_log = logging.getLogger(__name__)


class ErrorView(base.TemplateView):
    error_message = None
    error_css_class = "warning"
    error_code = None

    headline = _("Some sort of error or something")
    template_name = "inboxen/error.html"

    def dispatch(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        output = self.render_to_response(context, status=self.error_code)
        output.render()
        return output

    def get_context_data(self, **kwargs):
        kwargs["error_message"] = self.get_error_message()
        kwargs["error_css_class"] = self.get_error_css_class()
        kwargs["error_code"] = self.get_error_code()
        return super(ErrorView, self).get_context_data(**kwargs)

    def get_error_message(self):
        """Returns a short error message to be displayed to the user"""
        if self.error_message is None:
            raise ImproperlyConfigured("Set 'error_message' or override 'get_error_message'")
        else:
            return self.error_message

    def get_error_css_class(self):
        """Returns a CSS class to be used whatever template is being used"""
        return self.error_css_class

    def get_error_code(self):
        """Returns the numeric HTTP status code"""
        if self.error_code is None:
            raise ImproperlyConfigured("Set 'error_code' or override 'get_error_code'")
        else:
            return self.error_code

    def get_template_names(self):
        templates = ["{0}.html".format(self.get_error_code())]
        templates.extend(super(ErrorView, self).get_template_names())
        return templates


not_found = ErrorView.as_view(
    error_message=_("The page you requested cannot be found."),
    error_css_class="info",
    error_code=404,
    headline=_("Not Found"),
)


permission_denied = ErrorView.as_view(
    error_message=_("You do not have permission to view this page."),
    error_css_class="warning",
    error_code=403,
    headline=_("Permission Denied"),
)


server_error = ErrorView.as_view(
    error_message=_("There has been an error with our software. Our administrators have been notified."),
    error_css_class="danger",
    error_code=500,
    headline=_("Error"),
)


bad_request = ErrorView.as_view(
    error_message=_("I have no idea what you were trying to do, but you probably shouldn't be doing it!"),
    error_css_class="info",
    error_code=400,
    headline=_("No Idea"),
)


@csrf_exempt
@require_POST
def csp_report(request):
    """Simple CSP report view"""
    _log.critical("CSP Report: %s", request.body)
    return HttpResponse("")
