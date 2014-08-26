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

import json
import urllib

from django import http
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.views import generic
from django.utils import safestring

from website.views import base
from queue import tasks

from celery import exceptions
from celery.result import AsyncResult
from watson import models as watson_models

__all__ = ["SearchView", "SearchApiView"]

class SearchView(base.LoginRequiredMixin, base.CommonContextMixin,
                                    generic.ListView):
    """A specialised search view that splits results by model"""
    paginate_by = None
    template_name = "user/search.html"
    filter_limit = 10
    timeout = 5 # time to wait for results
    model = None # will be useful later, honest!

    query_param = "q"
    context_object_name = "search_results"

    quotes = [
        _("It'll be done soon, I'm sure."),
        _("Nearly there!"),
        _("Just a bit longer."),
        _("A biiiit longer."),
        ]

    def get(self, request, *args, **kwargs):
        self.query = self.get_query(request)
        return super(SearchView, self).get(request, *args, **kwargs)

    def get_cache_key(self):
        key = "{0}-{1}".format(self.request.user.username, self.query)
        return urllib.quote(key)

    def get_funny_quotes(self):
        """Concatenate quotes to be parsed as a JS array"""
        return safestring.mark_safe(json.dumps(self.quotes))

    def get_results(self):
        """Fetch result from either the cache or the queue

        Raises TimeoutError if results aren't ready by self.timeout"""
        result = cache.get(self.get_cache_key())
        if result is None:
            search_task = tasks.search.apply_async(args=[self.request.user.id, self.query])
            result = {"task": search_task.id}
        elif "task" in result:
            search_task = AsyncResult(result["task"])
        else:
            return result

        try:
            result = search_task.get(self.timeout)
        finally:
            # always update the cache at this point
            cache.set(self.get_cache_key(), result)

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
        if len(results["emails"]) > 0:
            queryset["emails"] = watson_models.SearchEntry.objects.filter(id__in=results["emails"]).prefetch_related("object")
        else:
            queryset["emails"] = []

        if len(results["inboxes"]) > 0:
            queryset["inboxes"] = watson_models.SearchEntry.objects.filter(id__in=results["inboxes"]).prefetch_related("object")
        else:
            queryset["inboxes"] = []

        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context["query"] = self.query
        context["funny"] = self.get_funny_quotes()

        # are we still waiting for results?
        context["waiting"] = len(context[self.context_object_name]) == 0

        return context

    def get_headline(self):
        return "%s: %s" % (_("Search"), self.query)

    def get_query_param(self):
        return self.query_param

    def get_query(self, request):
        get_query = request.GET.get(self.get_query_param(), "").strip()
        kwarg_query = self.kwargs.get(self.get_query_param(), "").strip()
        return kwarg_query or get_query


class SearchApiView(SearchView):
    """Check to see if a search is running or not"""
    def get(self, request, *args, **kwargs):
        """Some WSGI implementations convert HEAD requests to GET requests.

        It's very annoying
        """
        self.query = self.get_query(request)
        result = cache.get(self.get_cache_key())
        if result is not None and "task" in result:
            search_task = AsyncResult(result["task"])
            try:
                search_task.get(self.timeout)
            except exceptions.TimeoutError:
                return http.HttpResponse(status=202) # 202: still waiting for task
            return http.HttpResponse(status=201) # 201: search results ready
        elif result is not None:
            return http.HttpResponse(status=201) # 201: search results ready
        else:
            return http.HttpResponseBadRequest() # 400: no search is being performed
