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

from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import safestring

from pytz import utc
import markdown

class BlogPost(models.Model):
    """Basic blog post, body stored as MarkDown"""
    subject = models.CharField(max_length=512)
    body = models.TextField()
    date = models.DateTimeField('posted', null=True, blank=True)
    modified = models.DateTimeField('modified', auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    draft = models.BooleanField(default=True)

    @property
    def rendered_body(self):
        """Render MarkDown to HTML"""
        return safestring.mark_safe(markdown.markdown(self.body))

    def __unicode__(self):
        draft = ""
        if self.draft:
            draft = " (draft)"
        return u"%s%s" % (self.date, draft)

    class Meta:
        ordering = ["-date"]

@receiver(pre_save, sender=BlogPost, dispatch_uid="blog_date_draft_checker")
def published_checker(sender, instance=None, **kwargs):
    if not instance.draft and instance.date is None:
        instance.date = datetime.now(utc)
