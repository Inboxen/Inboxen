##
#    Copyright (C) 2017 Jessica Tallon & Matt Molyneaux
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

from django.db import models
from django.utils import safestring
from django.utils.functional import cached_property
from lxml.html.clean import Cleaner
import markdown
import six

from cms.widgets import RichTextInput

# default whitelists are actually stricter than we need in most cases, but it's
# easy enough to do DEFAULT_BLAH + ["new value"]
DEFAULT_ALLOW_TAGS = ["p", "a", "i", "b", "em", "strong", "ol", "ul", "li", "pre", "code"]
DEFAULT_SAFE_ATTRS = ["href"]
DEFAULT_MARKDOWN_EXTENSIONS = []
DEFAULT_MARKDOWN_EXTENSION_CONFIGS = {}


class HTML(six.text_type):
    # Unicode subclass so that it looks like a normal unicode object to the
    # rest of Django, but still has a nice render method. Avoids having to
    # write masses of conversion methods to make sure the database gets an
    # object type it understands.
    def __new__(cls, text, allow_tags, safe_attrs, extensions=None, extension_configs=None):
        # call unicode directly, because super(HTML, HTML) will look wrong
        text = six.text_type.__new__(cls, text)
        text.allow_tags = allow_tags
        text.safe_attrs = safe_attrs
        text.extensions = extensions or []
        text.extension_configs = extension_configs or {}

        return text

    @cached_property
    def render(self):
        if not self:
            return self

        cleaner = Cleaner(
            allow_tags=self.allow_tags,
            safe_attrs=self.safe_attrs,
            remove_unknown_tags=False,
            safe_attrs_only=True,
        )
        markdown_obj = markdown.Markdown(extensions=self.extensions, extension_configs=self.extension_configs)
        text = markdown_obj.convert(self)
        text = cleaner.clean_html(text)
        return safestring.mark_safe(text)


class TextDescriptor(object):
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, cls=None):
        if self.field.name in instance.__dict__:
            text = instance.__dict__[self.field.name]
        else:
            instance.refresh_from_db(fields=[self.field.name])
            text = getattr(instance, self.field.name)

        if type(text) != HTML:
            text = HTML(text, allow_tags=self.field.allow_tags, safe_attrs=self.field.safe_attrs,
                        extensions=self.field.extensions)
            instance.__dict__[self.field.name] = text
            return text
        else:
            return text

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value


class RichTextField(models.TextField):
    def __init__(self, **kwargs):
        self.allow_tags = kwargs.pop("allow_tags", DEFAULT_ALLOW_TAGS)
        self.safe_attrs = kwargs.pop("safe_attrs", DEFAULT_SAFE_ATTRS)
        self.extensions = kwargs.pop("extensions", DEFAULT_MARKDOWN_EXTENSIONS)

        super(RichTextField, self).__init__(**kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super(RichTextField, self).contribute_to_class(cls, name, **kwargs)

        setattr(cls, self.name, TextDescriptor(self))

    def deconstruct(self):
        name, path, args, kwargs = super(RichTextField, self).deconstruct()

        if self.allow_tags != DEFAULT_ALLOW_TAGS:
            kwargs["allow_tags"] = self.allow_tags

        if self.safe_attrs != DEFAULT_SAFE_ATTRS:
            kwargs["safe_attrs"] = self.safe_attrs

        if self.extensions != DEFAULT_MARKDOWN_EXTENSIONS:
            kwargs["extensions"] = self.extensions

        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {"widget": RichTextInput}
        defaults.update(kwargs)

        return super(RichTextField, self).formfield(**defaults)
