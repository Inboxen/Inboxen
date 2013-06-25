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
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from datetime import datetime

from pytz import utc
from bs4 import BeautifulSoup

from django.utils.safestring import mark_safe

from website.helper.user import user_profile, null_user
from inboxen.models import Email, Attachment, Alias, Header

def make_message(email):
    """ makes a python email.message.Message from our Email object """
    msg = MIMEMultipart("alternative")
    # looks to see if a HTML and plaintext is there
    attachments = []
    for attachment in email.attachments.all():
        if attachment.content_type in ["text/plain", "text/html"]:
            attachments.append(attachment)
    
    if len(attachments) >= 2:
        # we have multiples ones, we should use MIMEMultipart
        for attachment in attachments:
            try:
                gen_type, specific_type = attachment.content_type.split("/", 1)
            except ValueError:
                gen_type, specific_type = "application", "octet-stream"
            msg.attach(MIMEText(attachment.data, specific_type))
    elif attachments and attachments[0].content_type == "text/html":
        part = MIMEText(attachments[0].data, "html", "utf-8")
        msg.attach(part)
    elif attachments and attachments[0].content_type == "text/plain":
        part = MIMEText(attachments[0].data, "plain", "utf-8")
        msg.attach(part)
    else:
        # oh dear, set the body as nothing then
        part = MIMEText('', 'plain', "utf-8")
        msg.attach(part)

    # okay now deal with other attachments
    for attachment in email.attachments.all():
        if attachment in attachments:
            continue # we've already handled it
        # right now deal with it
        try:
            gen_type, specific_type = attachment.content_type.split("/", 1)
        except (AttributeError, IndexError):
            gen_type, specific_type = "application", "octet-stream" # generic
        if gen_type == "audio":
            attach = MIMEAudio(attachment.data, specific_type)
        elif gen_type == "image":
            attach = MIMEImage(attachment.data, specific_type)
        elif gen_type == "text":
            attach = MIMEText(attachment.data, specific_type, "utf-8")
        else:
            attach = MIMEBase(gen_type, specific_type)
            attach.set_payload(attachment.data)
            encoders.encode_base64(attach)
 
        attach.add_header("Content-Disposition", "attachment", filename=attachment.content_disposition)
        msg.attach(attach)

    # now add the headers
    for header in email.headers.all():
        msg[header.name] = header.data
   
    if email.body:
        msg["body"] = email.body
 
    return msg
    

def clean_html(email):
    email = BeautifulSoup(email, "lxml")
    for elem in email.findAll(['script','link']):
        elem.extract()
    email = email.prettify()
    return email

def send_email(alias, sender, subject=None, body="", attachments=[]):
    """ Sends an email to an internal alias

    Expects an alias object
    """

    email = Email(
        user=alias.user,
        inbox=alias,
        recieved_date=datetime.now(utc)
    )

    if body:
        email.body = body

    email.save()

    sender = Header(
        name="From",
        data=sender,
    )

    sender.save()

    email.headers.add(sender)

    if subject:
        subject = Header(
            name="Subject",
            data=subject
        )

        subject.save()

        email.headers.add(subject)

    for attachment in attachments:
        email.attachments.add(attachment)

    email.save()

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

    email_id = int(email_id, 16)


    # quick fix, allows staff to read any message, not just their own
    # not sure if we really want that - M
    if user.is_staff:
        email = Email.objects.get(id=email_id)
    else:
        email = Email.objects.get(id=email_id, user=user)
    
    message = {
        "date":email.recieved_date
    }

    if read:
        email.read = True
        email.save()

    plain_attachments = email.attachments.filter(content_type="text/plain")
    html_attachments = email.attachments.filter(content_type="text/html")
    
    message["inbox"] = email.inbox

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
