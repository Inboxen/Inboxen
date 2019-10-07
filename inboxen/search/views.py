##
#    Copyright (C) 2014, 2018 Jessica Tallon & Matt Molyneaux
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

from celery import exceptions
from celery.result import AsyncResult
from django import http
from django.conf import settings
from django.core.cache import cache
from django.db.models import Case, When
from django.utils.functional import cached_property
from django.views.decorators.http import require_http_methods

from inboxen.search import tasks
from inboxen.search.utils import create_search_cache_key

TIMEOUT = 1


class SearchMixin:
    timeout = TIMEOUT  # time to wait for results

    def dispatch(self, request, *args, **kwargs):
        self.query, self.last_item, self.first_item = self.get_query(request)
        return super().dispatch(request, *args, **kwargs)

    def get_cache_key(self):
        return create_search_cache_key(self.request.user.id, self.query, self.first_item, self.last_item)

    @cached_property
    def results(self):
        """Fetch result from either the cache or the queue

        Raises TimeoutError if results aren't ready by self.timeout
        """
        if self.query == "":
            return {}

        result = cache.get(self.get_cache_key())
        if result is None or settings.CELERY_TASK_ALWAYS_EAGER:
            if self.last_item:
                task_kwargs = {"after": self.last_item}
            else:
                task_kwargs = {"before": self.first_item}
            task_args = [self.request.user.id, self.query, self.model._meta.label]
            search_task = tasks.search.apply_async(args=task_args, kwargs=task_kwargs)
            result = {"task": search_task.id}
            cache.set(self.get_cache_key(), result, tasks.SEARCH_TIMEOUT)
        elif "task" in result:
            search_task = AsyncResult(result["task"])
        else:
            return result

        try:
            return search_task.get(self.timeout)
        except exceptions.TimeoutError:
            return result or {}

    def get_search_queryset(self):
        if len(self.results.get("results", [])) > 0:
            qs = self.model.objects.filter(id__in=self.results["results"])
            qs = qs.order_by(Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(self.results["results"])]))
        else:
            qs = self.model.objects.none()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query
        context["token"] = self.get_cache_key()

        # are we still waiting for results?
        if self.query == "":
            context["waiting"] = False
        else:
            context["waiting"] = "task" in self.results

        if len(self.results.get("results", [])) > 0:
            context.update({
                "has_next": self.results["has_next"],
                "has_previous": self.results["has_previous"],
                "last": self.results.get("last", None),
                "first": self.results.get("first", None),
            })

        return context

    def get_query(self, request):
        get_query = request.GET.get("q", "").strip()
        kwarg_query = self.kwargs.get("q", "").strip()
        return (
            kwarg_query or get_query,
            request.GET.get("after", "").strip() or None,
            request.GET.get("before", "") or None,
        )


@require_http_methods(["HEAD"])
def search_api(request):
    try:
        key = request.GET["token"]
    except KeyError:
        raise http.Http404

    result = cache.get(key)

    if result is not None and "task" in result:
        search_task = AsyncResult(result["task"])
        try:
            search_task.get(TIMEOUT)
        except exceptions.TimeoutError:
            return http.HttpResponse(status=202)  # 202: still waiting for task
        return http.HttpResponse(status=201)  # 201: search results ready
    elif result is not None:
        return http.HttpResponse(status=201)  # 201: search results ready
    else:
        return http.HttpResponseBadRequest()  # 400: no search is being performed
