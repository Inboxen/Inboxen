from django.conf import settings
from django.views import generic
from django.utils.translation import ugettext as _

class CommonContextMixin(object):
	title = ""

	def get_context_data(self, *args, **kwargs):
		context = super(CommonContextMixin, self).get_context_data(*args, **kwargs)
		context.setdefault("page", _(self.title))
		context.setdefault("settings", settings)
		context.setdefault("request", self.request)
		return context

class FileDownloadMixin(object):
	""" Provides a response for file downloading """

	file_filename = ""
	file_attachment = False
	file_contenttype = "application/octet-stream"
	file_status = 200


	def get_file_data(self):
		pass

	def render_to_response(self):
		# build the Content-Disposition header
		dispisition = []
		if self.file_attachment:
			dispisition.append("attachment")

		if self.file_filename:
			dispisition.append("filename={0}".format(self.file_filename))

		dispisition = "; ".join(dispisition)

		# make header object
		data = self.get_file_data()
		response = http.HttpResponse(
			content=data,
			status=self.status
		)

		response["Content-Length"] = len(data)
		response["Content-Disposition"] = dispisition
		return response

class TemplateView(CommonContextMixin, generic.TemplateView):
	""" django's templateview with some commonly needed context data """
	pass