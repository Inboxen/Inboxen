from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from tickets import models


class QuestionAdmin(ModelAdmin):
    model = models.Question
    menu_icon = 'help'
    list_display = ("subject", "author", "status")


modeladmin_register(QuestionAdmin)
