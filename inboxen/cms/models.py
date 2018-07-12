##
#    Copyright (C) 2013, 2014, 2015, 2016, 2017 Jessica Tallon & Matt Molyneaux
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
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import RegexURLResolver, reverse
from django.db import models
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey
from mptt.querysets import TreeQuerySet

from inboxen.cms.fields import (
    DEFAULT_ALLOW_TAGS,
    DEFAULT_MARKDOWN_EXTENSIONS,
    DEFAULT_MARKDOWN_EXTENSION_CONFIGS,
    DEFAULT_SAFE_ATTRS,
    RichTextField,
)
from inboxen import validators


HELP_PAGE_TAGS = DEFAULT_ALLOW_TAGS + ["h%s" % i for i in range(1, 6)]
HELP_PAGE_ATTRS = DEFAULT_SAFE_ATTRS + ["id"]
HELP_PAGE_EXTENSIONS = DEFAULT_MARKDOWN_EXTENSIONS + ["markdown.extensions.toc"]
HELP_PAGE_EXTENSION_CONFIGS = {"markdown.extensions.toc": {"anchorlink": True}}
# set default configs
for k, v in DEFAULT_MARKDOWN_EXTENSION_CONFIGS.items():
    HELP_PAGE_EXTENSION_CONFIGS.set_default(k, v)


class HelpQuerySet(TreeQuerySet):
    def in_menu(self):
        return self.filter(in_menu=True)

    def live(self):
        return self.filter(live=True)


class HelpManager(models.Manager.from_queryset(HelpQuerySet), TreeManager):
    pass


class HelpAbstractPage(MPTTModel):
    # managers on abstract models are inherited, managers on concrete models are not!
    objects = HelpManager()

    class Meta:
        abstract = True
        manager_inheritance_from_future = True


class HelpBasePage(HelpAbstractPage):
    # Much of this class is taken from Wagtail 1.12.1
    #
    # Copyright (c) 2014 Torchbox Ltd and individual contributors.
    # All rights reserved.
    #
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
    #     3. Neither the name of Torchbox nor the names of its contributors may be used
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

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    title = models.CharField(max_length=255, validators=[validators.ProhibitNullCharactersValidator()])
    description = models.TextField(blank=True, validators=[validators.ProhibitNullCharactersValidator()])

    live = models.BooleanField(default=False)
    in_menu = models.BooleanField(default=False)
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        related_name='cms_pages',
        on_delete=models.PROTECT,
    )
    slug = models.SlugField(max_length=255, validators=[validators.ProhibitNullCharactersValidator()])
    url_cache = models.CharField(max_length=255, default="", validators=[validators.ProhibitNullCharactersValidator()])

    template = "cms/help_base.html"

    admin_fields = ("title", "description", "slug", "live", "in_menu")

    # None means anything is allowed, set to [] if you want to
    # disallow this model from having any parent or children
    allowed_parents = None
    allowed_children = None

    @cached_property
    def url(self):
        # generate_url doesn't cache the url to url_cache (because we don't
        # know if we're going to save), so this property is a *cached* property
        # so we never call generate_url twice
        if self.url_cache:
            return self.url_cache
        else:
            return self.generate_url()

    def generate_url(self):
        if self.parent:
            return self.parent.url + self.slug + "/"
        else:
            return settings.CMS_ROOT_URL

    @cached_property
    def specific(self):
        """
        Return this page in its most specific subclassed form.
        """
        # the ContentType.objects manager keeps a cache, so this should potentially
        # avoid a database lookup over doing self.content_type. I think.
        content_type = ContentType.objects.get_for_id(self.content_type_id)
        model_class = content_type.model_class()
        if model_class is None:
            # Cannot locate a model class for this content type. This might happen
            # if the codebase and database are out of sync (e.g. the model exists
            # on a different git branch and we haven't rolled back migrations before
            # switching branches); if so, the best we can do is return the page
            # unchanged.
            return self
        elif isinstance(self, model_class):
            # self is already the an instance of the most specific class
            return self
        else:
            return content_type.get_object_for_this_type(id=self.id)

    @cached_property
    def specific_class(self):
        """
        Return the class that this page would be if instantiated in its
        most specific form
        """
        content_type = ContentType.objects.get_for_id(self.content_type_id)
        return content_type.model_class()

    def route(self, request, path_components):
        if path_components:
            # request is for a child of this page
            child_slug = path_components[0]
            remaining_components = path_components[1:]

            try:
                subpage = self.get_children().get(slug=child_slug)
            except HelpBasePage.DoesNotExist:
                raise Http404

            return subpage.specific.route(request, remaining_components)

        else:
            # request is for this very page
            if self.live:
                return (self, [], {})
            else:
                raise Http404

    def serve(self, request, *args, **kwargs):
        assert type(self) != HelpBasePage, "serve method was called directly on a HelpBasePage object"

        return TemplateResponse(
            request,
            self.template,
            self.get_context(request, *args, **kwargs)
        )

    def get_context(self, request, *args, **kwargs):
        return {
            "page": self,
        }

    def save(self, *args, **kwargs):
        self.url_cache = self.generate_url()
        return super(HelpBasePage, self).save(*args, **kwargs)

    class Meta:
        manager_inheritance_from_future = True
        unique_together = ("slug", "parent")


class HelpIndex(HelpBasePage):
    template = "cms/help_index.html"

    def get_context(self, request, *args, **kwargs):
        context = super(HelpIndex, self).get_context(request, *args, **kwargs)
        context["menu"] = self.get_children().live().in_menu()

        return context

    class Meta:
        manager_inheritance_from_future = True


class AppPage(HelpBasePage):
    APP_CHOICES = (
        ("tickets.urls", "Tickets"),
    )
    APP_PREFIX = "inboxen."
    app = models.CharField(max_length=255, unique=True, choices=APP_CHOICES)

    admin_fields = HelpBasePage.admin_fields + ("app",)

    allowed_children = []

    def route(self, request, path_components):
        if not self.live:
            raise Http404

        resolver = RegexURLResolver(r"^", self.APP_PREFIX + self.app)
        path = request.path[len(self.url):]
        view, args, kwargs = resolver.resolve(path)

        self._view = view
        return (self, args, kwargs)

    def serve(self, request, *args, **kwargs):
        request.page = self
        return self._view(request, *args, **kwargs)

    def reverse(self, viewname, args=None, kwargs=None):
        """Gives reverse URL for view name relative to page"""
        return reverse(viewname, urlconf=self.APP_PREFIX + self.app, args=args, kwargs=kwargs)

    class Meta:
        manager_inheritance_from_future = True


class HelpPage(HelpBasePage):
    body = RichTextField(
        help_text=_("Markdown text, supports the TOC extension."),
        validators=[validators.ProhibitNullCharactersValidator()],
        allow_tags=HELP_PAGE_TAGS,
        safe_attrs=HELP_PAGE_ATTRS,
        extensions=HELP_PAGE_EXTENSIONS,
    )

    template = "cms/help_page.html"

    admin_fields = HelpBasePage.admin_fields + ("body",)

    class Meta:
        manager_inheritance_from_future = True


##
#   These models aren't currently used
##

class PeoplePage(HelpBasePage):
    intro_paragraph = RichTextField(
        blank=True,
        help_text=_("Text at the top of the page. Supports standard markdown."),
        validators=[validators.ProhibitNullCharactersValidator()],
    )

    template = "cms/people_page.html"

    admin_fields = HelpBasePage.admin_fields + ("intro_paragraph",)

    class Meta:
        manager_inheritance_from_future = True


class PersonInfo(models.Model):
    page = models.ForeignKey(PeoplePage, related_name="people", editable=False)
    ordinal = models.IntegerField(null=True, blank=True, editable=False)
    name = models.CharField(max_length=255, validators=[validators.ProhibitNullCharactersValidator()])
    body = RichTextField(validators=[validators.ProhibitNullCharactersValidator()])
    image = models.ForeignKey(
        "cms.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        ordering = ["ordinal"]


class Image(models.Model):
    title = models.CharField(max_length=255, validators=[validators.ProhibitNullCharactersValidator()])

    file = models.ImageField(width_field="width", height_field="height")
    width = models.IntegerField(editable=False)
    height = models.IntegerField(editable=False)

    created = models.DateTimeField(auto_now_add=True)
    collection = models.CharField(max_length=255, validators=[validators.ProhibitNullCharactersValidator()])
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="cms_images",
    )
