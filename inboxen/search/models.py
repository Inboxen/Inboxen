##
#    Copyright (C) 2019 Jessica Tallon & Matt Molyneaux
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

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector, SearchVectorField
from django.db import models
from django.db.models.expressions import Value


class SearchQuerySet(models.QuerySet):
    def search(self, search_term):
        query = SearchQuery(search_term, config=settings.SEARCH_CONFIG)
        return self.annotate(rank=SearchRank(models.F("search_tsv"), query)).filter(rank__gte=0.1).order_by("-rank")


class SearchManager(models.Manager.from_queryset(SearchQuerySet)):
    pass


class SearchableAbstract(models.Model):
    class Meta:
        abstract = True
        indexes = [GinIndex(fields=["search_tsv"])]

    objects = SearchManager()

    search_tsv = SearchVectorField(null=True)

    def update_search(self):
        vectors = SearchVector(Value("", output_field=models.TextField()), config=settings.SEARCH_CONFIG)
        for weight in ["a", "b", "c", "d"]:
            if hasattr(self, "index_search_{}".format(weight)):
                content = getattr(self, "index_search_{}".format(weight))()
                vectors = vectors + SearchVector(Value(content, output_field=models.TextField()),
                                                 config=settings.SEARCH_CONFIG, weight=weight.upper())

        self.search_tsv = vectors


class SearchTestModel(SearchableAbstract):
    """This model is only used during tests

    However, it appears difficult to have an app with migrations that are used
    in tests *and* have a model without migrations used in tests. So this model
    sits here.
    """
    field1 = models.TextField()
    field2 = models.TextField()

    class Meta:
        app_label = "search"

    def index_search_a(self):
        return self.field1

    def index_search_b(self):
        return self.field2

    def __repr__(self):
        return "<{}: {} {}".format(self.__class__.__name__,
                                   self.field1, self.field2)
