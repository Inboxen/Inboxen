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
