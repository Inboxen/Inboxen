##
#    Copyright (C) 2014 Jessica Tallon, Matt Molyneaux
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

from django.views import generic
from django.utils.translation import ugettext as _

from braces.views import LoginRequiredMixin, SetHeadlineMixin, StaticContextMixin

__all__ = ["LoginRequiredMixin", "CommonContextMixin", "TemplateView"]

class CommonMixin(SetHeadlineMixin):
    """Common items that are used in all views

    Can be given headline (string)
    """
    pass

class TemplateView(CommonContextMixin, generic.TemplateView):
    """ django's templateview with some commonly needed context data """
    pass
