from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from tickets import models, views


class QuestionAdmin(ModelAdmin):
    model = models.Question
    menu_icon = 'help'
    list_display = ("subject", "author", "status")
    edit_view_class = views.QuestionAdminEditView

modeladmin_register(QuestionAdmin)
