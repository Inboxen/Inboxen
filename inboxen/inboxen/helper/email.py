##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen front-end.
#
#    Inboxen front-end is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen front-end is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen front-end.  If not, see <http://www.gnu.org/licenses/>.
##
from datetime import datetime
from pytz import utc

from django.utils.safestring import mark_safe

from inboxen.models import Email, Attachment, Alias, Header
from inboxen.helper.user import user_profile

def send_email(user, alias, sender, subject=None, body=""):
    """ Sends an email to an internal alias """
    email = Email(
        read=False,
        user=user,
        inbox=alias,
        recieved_date=datetime.now(utc)
    )

    if body:
        email.body = body

    sender = Header(
        name="From",
        data=sender,
    )

    email.headers.add(sender)

    if subject:
        subject = Header(
            name="Subject",
            data=subject
        )

        email.headers.add(subject)

    email.send()

    





def get_email(user, email_id, preference=None, read=False):
    """ Gets an email based on user preferences and id of the email """
    # does the user want HTML emails?
    # 0 - don't ever give HTML
    # 1 - prefer plain text but if not HTML
    # 2 - prefer HTML
    if None == preference:
        html_preference = user_profile(user).html_preference
    else:
        html_preference = int(preference)

    email = Email.objects.get(id=email_id)
    
    message = {
        "date":email.recieved_date
    }

    if read:
        email.read = True
        email.save()

    plain_attachments = email.attachments.filter(content_type="text/plain")
    html_attachments = email.attachments.filter(content_type="text/html")
    
    if email.body and (html_preference < 2 or not html_attachments.exists()):
        # I think we can give them this?
        # I hope noone sets HTML in the email.body
        message["body"] = email.body
        message["attachments"] = email.attachments.all()
        message["plain"] = True
     
    if preference < 2 and plain_attachments.exists():
        body = plain_attachments[0]
        message["body"] = body
        message["attachments"] = email.attachments.all()
        message["plain"] = True
    
    if preference == 0 and html_attachments.exists():
        # we have an html but we don't wanna see
        # we'll strip the tags out...
        message["body"] = ""
        message["attachments"] = email.attachments.all()
        message["plain"] = True

    if html_attachments.exists():
        message["body"] = mark_safe(html_attachments[0].data)
        message["attachments"] = email.attachments.all()
        message["plain"] = False

    # handle headers
    for header in email.headers.all():
        if header.name.lower() == "subject":
            message["subject"] = header.data
        elif header.name.lower() == "from":
            message["from"] = header.data

    # ensure subject has been set
    if "subject" not in message:
        message["subject"] = "(No Subject)"

    return message 
