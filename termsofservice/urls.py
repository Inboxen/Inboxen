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

from django.conf import urls
from django.utils.translation import ugettext as _

from website.views import base as views

# If you're debugging regex, test it out on http://www.debuggex.com/ first - M
urlpatterns = urls.patterns('',
    urls.url(r'^tos/$', views.TemplateView.as_view(template_name="termsofservice/tos.html", headline=_("Terms Of Service")), name='termsofservice-tos'),
    urls.url(r'^who/$', views.TemplateView.as_view(template_name="termsofservice/who.html", headline=_("Who Are We?")), name='termsofservice-who'),
    )
