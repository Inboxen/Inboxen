##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from django.views import generic

from inboxen import models

class DeleteInboxView(generic.DeleteView):
	models = models.Email
	pk_url_kwarg = "id"

	def get_object(self, *args, **kwargs):
		# Convert the id from base 16 to 10
		self.kwargs[self.pk_url_kwargs] = int(self.kwargs[self.pk_url_kwargs], 16)
		return super(DeleteInboxView, self).get_object(*args, **kwargs)

	def get_success_url(self):
		return "/inbox/{0}/".format(self.kwargs["email_address"])

	def get_queryset(self, *args, **kwargs):
		queryset = super(DeleteInboxView, self).get_queryset(*args, **kwargs)
		queryset = queryset.filter(inbox__user=self.request.user).only("id")
		return queryset

