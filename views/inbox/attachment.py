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

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect

from inboxen.models import Attachment

@login_required
def download(request, attachmentid, method="download"):
    try:
        attachment = Attachment.objects.get(id=attachmentid)
    except Attachment.DoesNotExist:
    	# this should be an error
        return HttpResponseRedirect("/user/profile")

    response = HttpResponse(attachment.data, content_type=attachment.content_type)
    response["Content-Disposition"] = "filename=attachment-%s" % attachmentid
    if method == "download":
        response["Content-Disposition"] = "attachment; %s" % response["Content-Disposition"]

    return response
