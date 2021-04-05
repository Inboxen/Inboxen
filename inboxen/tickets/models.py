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

from django.conf import settings
from django.db import models
from django.utils import safestring
from django.utils.translation import gettext_lazy as _
from lxml.html.clean import Cleaner
import markdown

from inboxen import validators
from inboxen.tickets import managers


class RenderBodyMixin(object):
    def render_body(self):
        if not self.body:
            return ""

        cleaner = Cleaner(
            allow_tags=["p", "a", "i", "b", "em", "strong", "ol", "ul", "li", "pre", "code"],
            safe_attrs=["href"],
            remove_unknown_tags=False,
            safe_attrs_only=True,
        )
        body = markdown.markdown(self.body)
        body = cleaner.clean_html(body)
        return safestring.mark_safe(body)


class Question(models.Model, RenderBodyMixin):
    # status contants
    NEW = 0
    IN_PROGRESS = 1
    NEED_INFO = 2
    RESOLVED = 3

    # status choices
    STATUS_CHOICES = (
        (NEW, _("New")),
        (IN_PROGRESS, _("In progress")),
        (NEED_INFO, _("Need more info")),
        (RESOLVED, _("Resolved")),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    subject = models.CharField(max_length=512, validators=[validators.ProhibitNullCharactersValidator()])
    body = models.TextField(validators=[validators.ProhibitNullCharactersValidator()])

    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=NEW, db_index=True)

    objects = managers.QuestionQuerySet.as_manager()

    @property
    def last_activity(self):
        """Return the lastest activity of this Question

        Expects the attribute "last_response_date" to be annotated
        """
        # TODO turn this property into an annotation
        if getattr(self, "last_response_date", None) is not None and self.last_response_date > self.last_modified:
            return self.last_response_date
        else:
            return self.last_modified

    def __str__(self):
        return u"%s from %s" % (self.subject, self.author)

    class Meta:
        ordering = ["-date"]


class Response(models.Model, RenderBodyMixin):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True, db_index=True)

    body = models.TextField(validators=[validators.ProhibitNullCharactersValidator()])

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return u"Response to %s from %s" % (self.question, self.author)
