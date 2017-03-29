from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from inboxen import models


class RequestPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False


class DomainAdmin(ModelAdmin):
    model = models.Domain
    menu_icon = 'snippet'
    list_display = ("domain", "owner", "enabled")


class RequestAdmin(ModelAdmin):
    model = models.Request
    menu_icon = 'arrow-up-big'
    list_display = ("requester", "date", "amount", "succeeded")
    permission_helper_class = RequestPermissionHelper


modeladmin_register(DomainAdmin)
modeladmin_register(RequestAdmin)
