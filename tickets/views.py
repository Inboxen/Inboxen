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
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views import generic

from braces.views import LoginRequiredMixin
from wagtail.contrib.modeladmin.views import EditView

from cms.utils import app_reverse
from tickets import forms, models


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


class QuestionHomeView(LoginRequiredMixin, generic.ListView, FormMixin):
    """List of questions that belong to current user"""
    paginate_by = 10
    model = models.Question
    form_class = forms.QuestionForm
    template_name = "tickets/question_home.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()

        return super(QuestionHomeView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(QuestionHomeView, self).get_context_data(**kwargs)
        context["open"] = self.get_queryset().open()[:self.paginate_by]
        context["closed"] = self.get_queryset().closed()[:self.paginate_by]

        return context

    def get_queryset(self):
        qs = super(QuestionHomeView, self).get_queryset()
        qs = qs.filter(author=self.request.user).select_related("author")
        qs = qs.annotate(response_count=Count("response__id"), last_response_date=Max("response__date"))

        return qs

    def get_success_url(self):
        return app_reverse(self.request.page, self.request.site, "tickets-detail", kwargs={"pk": self.object.pk})


class QuestionListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 50
    model = models.Question

    def get_context_data(self, **kwargs):
        context = super(QuestionListView, self).get_context_data(**kwargs)
        context["status"] = self.kwargs.get("status", "").title()

        return context

    def get_queryset(self):
        qs = super(QuestionListView, self).get_queryset()

        # filter statuses
        status = self.kwargs["status"].upper()
        if status == "OPEN":
            qs = qs.open()
        elif status == "CLOSED":
            qs = qs.closed()
        else:
            raise Http404

        qs = qs.filter(author=self.request.user).select_related("author")
        return qs.annotate(response_count=Count("response__id"), last_response_date=Max("response__date"))


class QuestionDetailView(LoginRequiredMixin, generic.DetailView, FormMixin):
    """View and respond to Question"""
    model = models.Question
    form_class = forms.ResponseForm

    def get_form_kwargs(self):
        kwargs = super(QuestionDetailView, self).get_form_kwargs()
        kwargs["author"] = self.request.user
        kwargs["question"] = self.object

        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super(QuestionDetailView, self).get_context_data(**kwargs)
        kwargs.setdefault("responses", self.get_responses())
        return kwargs

    def get_queryset(self):
        qs = super(QuestionDetailView, self).get_queryset()
        return qs.filter(author=self.request.user).select_related("author")

    def get_success_url(self):
        return app_reverse(self.request.page, self.request.site, "tickets-detail", kwargs={"pk": self.object.pk})

    def get_responses(self):
        return self.object.response_set.select_related("author").all()

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        return super(QuestionDetailView, self).post(*args, **kwargs)


class QuestionAdminEditView(EditView):
    """View for modeladmin "edit" view"""
    def get_form_class(self):
        return forms.ResponseAdminForm

    def get_form_kwargs(self):
        kwargs = super(QuestionAdminEditView, self).get_form_kwargs()
        kwargs["author"] = self.request.user
        kwargs["question"] = kwargs["instance"]
        del kwargs["instance"]

        return kwargs

    def get_edit_handler_class(self):
        """Return a fake edit_handler because we're not using it"""
        class FakeHandler(object):
            def __init__(self, *args, **kwargs):
                pass

        return FakeHandler
