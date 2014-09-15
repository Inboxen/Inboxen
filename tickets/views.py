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

from django.core import urlresolvers
from django.db.models import Count, Max
from django.utils.translation import ugettext as _
from django.views import generic

from braces.views import StaffuserRequiredMixin

from tickets import forms, models
from website.views import base

class FormMixin(generic.edit.FormMixin):
    """FormMixin specific to Tickets"""
    def get_context_data(self, **kwargs):
        kwargs = super(FormMixin, self).get_context_data(**kwargs)

        form_class = self.get_form_class()
        kwargs["form"] = self.get_form(form_class)

        return kwargs

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class QuestionListBaseView(base.CommonContextMixin, generic.ListView, FormMixin):
    """Base list view of questions. Subclass it to restrict to a single user's
    questions or admins view.
    """
    paginate_by = 50
    model = models.Question
    headline = _("Tickets")
    form_class = forms.QuestionForm

    # ugly
    # same order as in models.py
    choices = ("NEW", "IN_PROGRESS", "NEED_INFO", "RESOLVED")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super(QuestionListBaseView, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        if not "status" in self.kwargs:
            self.kwargs["status"] = "!resolved"

        return super(QuestionListBaseView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = super(QuestionListBaseView, self).get_queryset()

        # filter statuses
        try:
            if self.kwargs["status"].startswith("!"):
                status = self.choices.index(self.kwargs["status"][1:].upper())
                qs = qs.exclude(status=status)
            else:
                status = self.choices.index(self.kwargs["status"].upper())
                qs = qs.filter(status=status)
        except ValueError:
            # or not
            pass

        return qs.select_related("author").annotate(response_count=Count("response__id"), last_response_date=Max("response__date"))

    def get_success_url(self):
        return urlresolvers.reverse("tickets-detail", kwargs={"pk": self.object.pk})

    def post(self, *args, **kwargs):
        # taken from Django 1.6.7: django/views/generic/list.py
        # Copyright (c) Django Software Foundation and individual contributors.
        # All rights reserved.
        # Redistribution and use in source and binary forms, with or without modification,
        # are permitted provided that the following conditions are met:
        #
        #     1. Redistributions of source code must retain the above copyright notice,
        #        this list of conditions and the following disclaimer.
        #
        #     2. Redistributions in binary form must reproduce the above copyright
        #        notice, this list of conditions and the following disclaimer in the
        #        documentation and/or other materials provided with the distribution.
        #
        #     3. Neither the name of Django nor the names of its contributors may be used
        #        to endorse or promote products derived from this software without
        #        specific prior written permission.
        #
        # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
        # ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
        # WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        # DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
        # ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
        # (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
        # LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
        # ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
        # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
        # SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                        % {'class_name': self.__class__.__name__})
        return super(QuestionListBaseView, self).post(*args, **kwargs)

class QuestionDetailBaseView(base.CommonContextMixin, generic.DetailView, FormMixin):
    """Base detail view of a question. Subclass it to restrict to restrict to
    author or admins view.
    """
    model = models.Question
    form_class = forms.ResponseForm

    def form_valid(self, form):
        response = form.save(commit=False)
        response.author = self.request.user
        response.question = self.object
        response.save()
        return super(QuestionDetailBaseView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs = super(QuestionDetailBaseView, self).get_context_data(**kwargs)
        kwargs.setdefault("responses", self.get_responses())
        return kwargs

    def get_headline(self):
        ticket = _("Ticket")
        return "{0}: {1}".format(ticket, self.object.subject)

    def get_queryset(self):
        qs = super(QuestionDetailBaseView, self).get_queryset()
        return qs.select_related("author")

    def get_success_url(self):
        return urlresolvers.reverse("tickets-detail", kwargs={"pk": self.object.pk})

    def get_responses(self):
        return self.object.response_set.all()

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        return super(QuestionDetailBaseView, self).post(*args, **kwargs)

class QuestionListView(base.LoginRequiredMixin, QuestionListBaseView):
    """Question list, restricted to the current user"""
    def get_queryset(self):
        qs = super(QuestionListView, self).get_queryset()
        return qs.filter(author=self.request.user)

class QuestionDetailView(base.LoginRequiredMixin, QuestionDetailBaseView):
    """Question detail, restricted to the current user"""
    def get_queryset(self):
        qs = super(QuestionDetailView, self).get_queryset()
        return qs.filter(author=self.request.user)

class QuestionListAdminView(base.LoginRequiredMixin, StaffuserRequiredMixin, QuestionListBaseView):
    """Admin's view of Questions"""
    raise_exception = True

class QuestionDetailAdminView(base.LoginRequiredMixin, StaffuserRequiredMixin, QuestionDetailBaseView):
    """Admin's view of a single Question"""
    raise_exception = True
