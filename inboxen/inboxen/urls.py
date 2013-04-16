from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'inboxen.views.home', name='home'),
    url(r'^login/', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^register/', 'inboxen.views.register', name="register"),
    url(r'^contact/', 'inboxen.views.contact', name="Contact"),
    url(r'^accounts/profile/', 'inboxen.views.profile', name='profile'),
    url(r'^add-alias/', 'inboxen.views.add_alias'),
    url(r'^settings/', 'inboxen.views.settings'),
    url(r'^inbox/(?P<inbox>\w+)@(?P<domain>\w+)/$', 'inboxen.views.inbox'),
    url(r'^logout/', 'inboxen.views.logout_user', name="logout"),
    url(r'^inbox/(?P<email>[a-zA-Z0-9@\.]+)', 'inboxen.views.specific'),
    url(r'^delete/(?P<email>[a-zA-Z0-9@\.]+)', 'inboxen.views.delete_alias'),
    
    # API stuff.
    url(r'^api/alias/create', 'inboxen.api.alias_create'),
    url(r'^api/alias/delete', 'inboxen.api.alias_delete'),
    url(r'^api/alias', 'inboxen.api.alises'),

    # url(r'^inboxen/', include('inboxen.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
