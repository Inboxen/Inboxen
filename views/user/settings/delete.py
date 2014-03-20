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
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse_lazy

from website import forms
from website.views import base

from queue.delete.tasks import delete_account

class AccountDeletionView(base.CommonContextMixin, base.LoginRequiredMixin, generic.FormView):
    """ View to delete an account """

    form_class = forms.DeleteAccountForm
    success_url = reverse_lazy('index')
    template_name = "user/settings/delete.html"
    title = "Delete Account"

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(AccountDeletionView, self).get_form_kwargs(*args, **kwargs)
        kwargs.setdefault("request", self.request)
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        form.save()
        return super(AccountDeletionView, self).form_valid(form=form, *args, **kwargs)
