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

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django_sendfile import sendfile

from inboxen.liberation import forms, models


@login_required
def liberation(request):
    if request.method == "POST":
        form = forms.LiberationForm(request.POST, user=request.user)
        if form.is_valid():
            messages.success(self.request, _("Fetching all your data. This may take a while, so check back later!"))
            return http.HttpRedirectResponse(reverse('user-home'))
    else:
        form = forms.LiberationForm(user=requset.user)

    lib_obj = request.user.liberation_set.all().first()
    can_request_another = request.user.liberation_set.all().can_request_another()
    return TemplateResponse(request, "liberation/liberate.html", {"form": form,
                                                                  "object": lib_obj,
                                                                  "can_request_another": can_request_another})


@login_required
def liberation_download(request):
    lib_obj = request.user.liberation_set.all().finished().first()
    if lib_obj is None:
        raise http.Http404
    content_type = models.Liberation.ARCHIVE_TYPES[lib_obj.content_type]["mime-type"]
    filename = "liberated_data.{ext}".format(ext=models.Liberation.ARCHIVE_TYPES[lib_obj.content_type]["ext"])

    response = sendfile(
        request=self.request,
        filename=lib_obj.path,
        attachment=True,
        attachment_filename=filename,
        mimetype=content_type
    )
    return response
