from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'inboxen.views.home', name='home'),
    url(r'^login/', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^register/', 'inboxen.views.login.register', name="register"),
    url(r'^contact/', 'inboxen.views.contact', name="Contact"),
    url(r'^profile/', 'inboxen.views.profile.profile', name='profile'),
    url(r'^add-alias/', 'inboxen.views.alias.add_alias'),
    url(r'^settings/', 'inboxen.views.profile.settings'),
    url(r'^logout/', 'inboxen.views.login.logout_user', name="logout"),
    url(r'^inbox/(?P<email_address>[a-zA-Z0-9@\.]+)/(?P<emailid>\d+)', 'inboxen.views.inbox.read_email'),
    url(r'^inbox/(?P<email_address>[a-zA-Z0-9@\.]+)', 'inboxen.views.inbox.inbox'),
    url(r'^delete/(?P<email>[a-zA-Z0-9@\.]+)', 'inboxen.views.alias.delete_alias'),
 
    # API stuff.
    #url(r'^api/alias/create', 'inboxen.api.alias_create'),
    #url(r'^api/alias/delete', 'inboxen.api.alias_delete'),
    #url(r'^api/alias', 'inboxen.api.alises'),

    # url(r'^inboxen/', include('inboxen.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
