# -*- coding: utf-8 -*-
##
#    Copyright (C) 2013, 2014 Jessica Tallon & Matt Molyneaux
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
from django_extensions.db.fields import AutoSlugField

from inboxen import validators
from inboxen.cms.fields import DEFAULT_ALLOW_TAGS, DEFAULT_SAFE_ATTRS, RichTextField

BLOG_ALLOW_TAGS = DEFAULT_ALLOW_TAGS + ["img"]
BLOG_SAFE_ATTRS = DEFAULT_SAFE_ATTRS + ["src", "alt"]


class BlogPost(models.Model):
    """Basic blog post, body stored as MarkDown"""
    subject = models.CharField(max_length=512, validators=[validators.ProhibitNullCharactersValidator()])
    body = RichTextField(validators=[validators.ProhibitNullCharactersValidator()],
                         allow_tags=BLOG_ALLOW_TAGS, safe_attrs=BLOG_SAFE_ATTRS)
    date = models.DateTimeField('posted', null=True, blank=True, editable=False, db_index=True)
    modified = models.DateTimeField('modified', auto_now=True, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    draft = models.BooleanField(default=True)

    slug = AutoSlugField(populate_from="subject", max_length=64,
                         validators=[validators.ProhibitNullCharactersValidator()])

    def __str__(self):
        draft = u""
        if self.draft:
            draft = u" (draft)"

        if not self.subject:
            subject = u"(untitled)"
        elif len(self.subject) > 64:
            subject = u"%s…" % self.subject[:63]
        else:
            subject = self.subject

        return u"%s%s" % (subject, draft)

    class Meta:
        ordering = ["-date"]
