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

from django.db.models import Count
from django.utils.translation import ugettext as _
from django.views import generic

from tickets import forms, models
from website.views import base

class FormMixin(generic.edit.FormMixin):
    """FormMixin specific to Tickets"""
    def get_context_data(self, **kwargs):
        kwargs = super(FormMixin, self).get_context_data(**kwargs)

        form_class = self.get_form_class()
        kwargs["form"] = self.get_form(form_class)

        return kwargs

    def get_inital(self):
        initial = super(FormMixin, self).get_initial()
        initial.update({"author": self.request.user})

    def get_form_kwargs(self):
        kwargs = super(FormMixin, self).get_form_kwargs()
        kwargs.setdefault(request=self.request)
        return kwargs

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class QuestionListView(base.LoginRequiredMixin, base.CommonContextMixin, FormMixin, generic.ListView):
    paginate_by = 50
    model = models.Question
    headline = _("Tickets")
    form = forms.QuestionForm

    def get_queryset(self):
        qs = super(QuestionListView, self).get_queryset().filter(asker=self.request.user)
        return qs.select_related("asker").annotate(response_count=Count("response__id"))

class QuestionDetailView(base.LoginRequiredMixin, base.CommonContextMixin, FormMixin, generic.DetailView):
    model = models.Question
    form = forms.ResponseForm

    def get_context_data(self, **kwargs):
        kwargs = super(QuestionDetailView, self).get_context_data(**kwargs)
        kwargs.setdefault(responses=self.get_responses())

    def get_headline(self):
        ticket = _("Ticket")
        return "{0}: {1}".format(ticket, self.object.subject)

    def get_initial(self):
        initial = super(QuestionDetailView, self).get_initial()
        initial.update({"question": self.object})
        return initial

    def get_queryset(self):
        qs = super(QuestionListView, self).get_queryset().filter(asker=self.request.user)
        return qs.select_related("asker")

    def get_responses(self):
        return self.object.response_set.all()
