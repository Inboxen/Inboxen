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
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db.models import F
from lxml.html.clean import Cleaner

from inboxen.models import Email, Header

@login_required
def view(request, email_address, emailid):
    try:
        inbox = request.user.inbox_set.from_string(email=email_address)

        email = int(emailid, 16)
        email = Email.objects.get(id=email, flags=~Email.flags.deleted)
        email.update(flags=F('flags').bitand(Email.flags.read))
    except (Email.DoesNotExist, Inbox.DoesNotExist):
        return Http404

    headers = Header.objects.filter(part__email=email, part__parent=None)
    headers = headers.get_many("Subject", "From")

    email_obj = {}
    email_obj["subject"] = headers["Subject"]
    email_obj["from"] = headers["From"]
    email_obj["date"] = email.received_date

    attachments = []
    for part in email.parts:
        item = part.header_set.get_many("Content-Type", "Content-Disposition")
        item["id"] = part.id
        item["part"]
        item["parent"] = part.parent.id
        attachments.append(item)

    # find first text/html and first text/plain
    html = False
    plain = False
    for part in attachments:
        if not html and part["Content-Type"] == "text/html":
            html = part["part"]
        elif not plain and part["Content-Type"] == "text/plain":
            plain = part["part"]
        del part["part"]

    # if siblings, use html_preference
    if html["parent"] == plain["parent"]:
        pref = request.user.userprofile.html_preference
        if pref == 1:
            plain_message = True
            email["body"] = plain.body.data
        elif pref == 2:
            plain_message = False
            email["body"] = html.body.data

    # if not, which ever has the lower lft value
    elif not html and attachments.index(html) < attachments.index(plain):
        plain_message = False
        email["body"] = html.body.data
    elif not plain and attachments.index(html) > attachments.index(plain):
        plain_message = True
        email["body"] = plain.body.data

    if not plain_message:
        # Mail Pile uses this, give back if you come up with something better
        cleaner = Cleaner(page_structure=True, meta=True, links=True,
                   javascript=True, scripts=True, frames=True,
                   embedded=True, safe_attrs_only=True)
        email["body"] = cleaner(email["body"])

    context = {
        "page":email_obj["subject"],
        "email":email_obj,
        "plain_message":plain_message,
        "user":request.user,
    }
 
    return render(request, "inbox/email.html", context)
