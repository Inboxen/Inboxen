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

from pytz import utc
from datetime import datetime, timedelta

from django.shortcuts import render
from inboxen.models import Request

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

@login_required
@staff_member_required
def requests(request, page=1):
    
    # Lets get the opne requests
    requests = Request.objects.filter(succeeded=None)
    
    # set some flags so coloured tables works.
    old = datetime.now(utc) - timedelta(hours=12)
    ancent = datetime.now(utc) - timedelta(days=1) 

    for r in requests:
        if r.date < ancent:
            r.ancent = True
            continue
        else:
            r.ancent = False
        
        if r.date < old:
            r.old = True
            continue
        else:
            r.old = False
    
    context = {
        "page":"Admin",
        "requests":requests,
    }

    return render(request, "admin/requests.html", context)   
