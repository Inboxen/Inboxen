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
from sys import version_info
from types import UnicodeType

from pytz import utc
from bs4 import BeautifulSoup
from premailer import Premailer

from django.utils.safestring import mark_safe

from website.helper.user import user_profile, null_user
from inboxen.models import Email, Attachment, Alias, Header

# lxml doesn't seem to like WSGI, but premailer seems ok :s
if version_info[:2] == (2, 7):
    PARSER = "html.parser"
else:
    PARSER = "html5lib"

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
    """Condense style sheets into style attributes so it doesn't mess with
    Inboxen styles. Also, remove bad tags like <script>
    """

    if type(email) != UnicodeType:
        email = unicode(email, "utf-8")

    # premailer uses lxml, assuming it will accept any old crap
    # and no pretty printing! (we do that later)
    try:
        email = Premailer(email).transform(False)
    except Exception:
        pass
    email = BeautifulSoup(email, PARSER)

    # this doesn't filter out everything
    # TODO: whitelist tags and attributes
    elements = []
    blacklist = ['script','link','head']
    rename_to_div = ['html','body']
    elements.extend(blacklist)
    elements.extend(rename_to_div)

    for elem in email.findAll(elements):
        if elem.name in blacklist:
            elem.extract()
        elif elem.name in rename_to_div:
            elem.name = "div"

    email = email.prettify()

    return mark_safe(email)

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

    # grab first plaintext and html attachments, if they exist
    try:
        plain_attachment = email.attachments.filter(content_type="text/plain")
        plain_attachemt = plain_attachment[0].data
    except (KeyError, Attachment.DoesNotExist):
        plain_attachemt = None

    try:
        html_attachment = email.attachments.filter(content_type="text/html")
        html_attachment =html_attachment[0].data
    except (KeyError, Attachment.DoesNotExist):
        html_attachment = None

    # grab body content-type, if it has one
    try:
        body_content_type = email.headers.get(name="content-type")
    except Header.DoesNotExist:
        body_content_type = None

    message["inbox"] = email.inbox
    message["attachments"] = email.attachments.all()

    # 0 - never give html
    if html_preference == 0:
        message["plain"] = True
        if not email.body and plain_attachemt:
            message["body"] = plain_attachment
        else:
            message["body"] = email.body

    # 1 - prefer plain
    elif html_preference == 1:
        # prefer whatever is in the body
        if email.body:
            message["body"] = email.body
            message["plain"] = (body_content_type == "text/plain")
        # first plain mime-part
        elif plain_attachment:
            message["body"] = plain_attachment
            message["plain"] = True
        # first html mime-part
        elif html_attachment:
            message["body"] = html_attachment
            message["plain"] = False

    # 2 - prefer HTML
    elif html_preference == 2:
        # prefer html in the body
        if body_content_type == "text/html":
            message["body"] = email.body
            message["plain"] = False
        # first html mime-part
        elif html_attachment:
            message["body"] = html_attachment
            message["plain"] = False
        # fallback to plaintext, prefering body over mime-part
        elif not email.body:
            message["body"] = plain_attachment
            message["plain"] = True
        else:
            message["body"] = email.body
            message["plain"] = True

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
