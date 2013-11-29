##
#    Copyright (C) 2013 Jessica Tallon & Matthew Molyneaux
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from inboxen.models import PartList

@login_required
def download(request, attachmentid, method="download"):
    try:
        attachment = PartList.objects.select_related('body').get(id=attachmentid, email__inbox__user=request.user)
    except (PartList.DoesNotExist):
    	# this should be an error
        return HttpResponseRedirect("/user/home")

    data = attachment.body.data
    headers = attachment.header_set.select_related('name', 'data')
    headers = headers.filter(Q(name__name="Content-Type") | Q(name__name="Content-Disposition"))
    headers = dict((header.name, header.data) for header in headers)

    try:
        response = HttpResponse(data, content_type=headers["Content-Type"].split(";",1)[0])
        disposition = header["Content-Disposition"].split(";")[1]

        response["Content-Disposition"] = "filename={0}".format(disposition)
        if method == "download":
            response["Content-Disposition"] = "attachment; filename={0}".format(disposition)
    except (KeyError, IndexError):
        # headers are fooked, we'll just ignore them :)
        response = HttpResponse(data)
    finally:
        response["Content-Length"] = len(data)

    return response
