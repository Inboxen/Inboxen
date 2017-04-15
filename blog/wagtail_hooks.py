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

from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import CreateView, EditView

from blog.models import BlogPost


class InstanceAuthorMixin(object):
    def get_instance(self):
        instance = super(InstanceAuthorMixin, self).get_instance()
        if instance.author_id is None:
            instance.author = self.request.user
        return instance


class BlogCreateView(InstanceAuthorMixin, CreateView):
    pass


class BlogEditView(InstanceAuthorMixin, EditView):
    pass


class BlogAdmin(ModelAdmin):
    model = BlogPost
    menu_icon = 'edit'
    list_display = ("subject", "author", "date", "published")

    def published(self, obj):
        return not obj.draft
    published.short_description = "Published?"
    published.boolean = True

    create_view_class = BlogCreateView
    edit_view_class = BlogEditView


modeladmin_register(BlogAdmin)
