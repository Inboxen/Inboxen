from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from blog.models import BlogPost


class BlogAdmin(ModelAdmin):
    model = BlogPost
    menu_icon = 'edit'
    list_display = ("subject", "author", "date", "published")

    def published(self, obj):
        return not obj.draft
    published.short_description = "Published?"
    published.boolean = True


modeladmin_register(BlogAdmin)
