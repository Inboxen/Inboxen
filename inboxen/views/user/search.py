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

from braces.views import LoginRequiredMixin
from celery import exceptions
from celery.result import AsyncResult
from django import http
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Case, When
from django.views import generic
from watson import models as watson_models

from inboxen import models, tasks
from inboxen.search.utils import create_search_cache_key


__all__ = ["SearchView", "SearchApiView"]


class SearchView(LoginRequiredMixin, generic.ListView):
    """A specialised search view that splits results by model"""
    paginate_by = None
    template_name = "inboxen/user/search.html"
    filter_limit = 10
    timeout = 1  # time to wait for results
    model = None  # will be useful later, honest!

    context_object_name = "search_results"

    def get(self, request, *args, **kwargs):
        self.query, self.last_item, self.first_item = self.get_query(request)
        return super(SearchView, self).get(request, *args, **kwargs)

    def get_cache_key(self):
        return create_search_cache_key(self.request.user.id, self.query, self.first_item, self.last_item)

    def get_results(self):
        """Fetch result from either the cache or the queue

        Raises TimeoutError if results aren't ready by self.timeout
        """
        result = cache.get(self.get_cache_key())
        if result is None or settings.CELERY_TASK_ALWAYS_EAGER:
            if self.last_item:
                task_kwargs = {"after": self.last_item}
            else:
                task_kwargs = {"before": self.first_item}
            search_task = tasks.search.apply_async(args=[self.request.user.id, self.query], kwargs=task_kwargs)
            result = {"task": search_task.id}
            cache.set(self.get_cache_key(), result, tasks.SEARCH_TIMEOUT)
        elif "task" in result:
            search_task = AsyncResult(result["task"])
        else:
            return result

        result = search_task.get(self.timeout)

        return result

    def get_queryset(self):
        if self.query == "":
            return {}

        try:
            results = self.get_results()
        except exceptions.TimeoutError:
            # we're still waiting for results
            return {}

        queryset = {}

        # some rubbish about not liking empty sets during IN statements :\
        if len(results["results"]) > 0:
            qs = watson_models.SearchEntry.objects.filter(id__in=results["results"]).prefetch_related("object")
            qs = qs.order_by(Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(results["results"])]))
            queryset = {
                "results": qs,
                "has_next": results["has_next"],
                "has_previous": results["has_previous"],
                "last": results.get("last", None),
                "first": results.get("first", None),
            }
        else:
            queryset = {
                "results": [],
                "has_next": False,
                "has_previous": False,
                "last": None,
                "first": None,
            }

        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context["query"] = self.query

        # are we still waiting for results?
        if self.query == "":
            context["waiting"] = False
        else:
            context["waiting"] = len(context[self.context_object_name]) == 0

        context["content_types"] = {
            "inbox": ContentType.objects.get_for_model(models.Inbox),
            "email": ContentType.objects.get_for_model(models.Email),
        }

        return context

    def get_query(self, request):
        get_query = request.GET.get("q", "").strip()
        kwarg_query = self.kwargs.get("q", "").strip()
        return (
            kwarg_query or get_query,
            request.GET.get("after", "").strip() or None,
            request.GET.get("before", "") or None,
        )


class SearchApiView(SearchView):
    """Check to see if a search is running or not"""
    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)

    def head(self, request, *args, **kwargs):
        self.query, self.last_item, self.first_item = self.get_query(request)
        result = cache.get(self.get_cache_key())
        if result is not None and "task" in result:
            search_task = AsyncResult(result["task"])
            try:
                search_task.get(self.timeout)
            except exceptions.TimeoutError:
                return http.HttpResponse(status=202)  # 202: still waiting for task
            return http.HttpResponse(status=201)  # 201: search results ready
        elif result is not None:
            return http.HttpResponse(status=201)  # 201: search results ready
        else:
            return http.HttpResponseBadRequest()  # 400: no search is being performed
