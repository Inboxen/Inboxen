from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'inboxen.views.home', name='home'),
    url(r'^login/', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^accounts/profile', 'inboxen.views.profile', name='profile'),
    # url(r'^inboxen/', include('inboxen.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
