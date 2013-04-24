from django.contrib import admin
from django.contrib.sites.models import Site

from inboxen.models import Domain

admin.site.unregister(Site)

admin.site.register(Domain)
