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

from django.views import generic
from django.utils.translation import ugettext as _

from tickets import models
from website.views import base

class QuestionListView(LoginRequiredMixin, CommonContextMixin, generic.ListView):
    model = models.Question
    headline = _("Tickets")

    def get_queryset(self):
        qs = super(QuestionListView, self).get_queryset()
        return qs.select_related("asker")

class QuestionDetailView(LoginRequiredMixin, CommonContextMixin, generic.DetailView):
    model = models.Question

    def get_headline(self):
        ticket = _("Ticket")
        return "{0}: {1}".format(ticket, self.object.subject

    def get_queryset(self):
        qs = super(QuestionListView, self).get_queryset()
        return qs.select_related("asker")
