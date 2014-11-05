##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from website import forms
from website.views import base

__all__ = ["RestoreSelectView"]


class RestoreSelectView(base.CommonContextMixin, base.LoginRequiredMixin, generic.FormView):
    form_class = forms.RestoreSelectForm
    headline = _("Choose An Inbox To Restore")
    template_name = "user/account/restore.html"

    def get_success_url(self):
        return urlresolvers.reverse("user-restore", kwargs={"inbox": self.inbox.inbox, "domain": self.inbox.domain.domain})

    def get_form_kwargs(self, **kwargs):
        kwargs = super(RestoreSelectView, self).get_form_kwargs(**kwargs)
        kwargs.setdefault("request", self.request)
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        self.inbox = form.save()
        return super(RestoreSelectView, self).form_valid(form=form, *args, **kwargs)
