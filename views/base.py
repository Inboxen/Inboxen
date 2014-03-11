from django.conf import settings
from django.views import generic
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod

class CommonContextMixin(object):
	title = ""

	def get_context_data(self, *args, **kwargs):
		context = super(CommonContextMixin, self).get_context_data(*args, **kwargs)
		context.setdefault("page", _(self.title))
		context.setdefault("settings", settings)
		context.setdefault("request", self.request)
		return context

class TemplateView(CommonContextMixin, generic.TemplateView):
	""" django's templateview with some commonly needed context data """
	pass

class LoginRequiredMixin(object):
    @classonlymethod
    def as_view(cls, **initkwargs):
        return login_required(super(LoginRequiredMixin, cls).as_view(**initkwargs))
