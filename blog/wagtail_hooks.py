from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from blog.models import BlogPost


class BlogAdmin(ModelAdmin):
    model = BlogPost
    list_display = ("subject", "author", "date", "published")

    def published(self, obj):
        return not obj.draft
    published.short_description = "Published?"
    published.boolean = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # TODO: move this
        if db_field.name == 'author':
            kwargs["initial"] = request.user.id
            kwargs["queryset"] = get_user_model().objects.filter(Q(is_staff=True) | Q(is_superuser=True))

        return super(BlogAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


modeladmin_register(BlogAdmin)
