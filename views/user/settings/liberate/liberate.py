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

from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.http import HttpResponseRedirect

from queue.tasks import liberate as data_liberate

def liberate(request):
    if request.method == "POST":
        options = {}
        if "mailType" in request.POST:
            options["mailType"] = request.POST["mailType"]
        if "compressType" in request.POST:
            options["compressType"] = request.POST["compressType"]

        data_liberate.delay(request.user, options=options)
        message = _("We're liberating! You should recieve an email shortly with your data in it ^_^")
        request.session["messages"] = [message]
        return HttpResponseRedirect("/user/profile")    


    context = {
        "page":_("Liberate your data"),
    }
    
    return render(request, "user/settings/liberate/liberate.html", context)
