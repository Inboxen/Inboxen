from django.utils.safestring import mark_safe

from inboxen.models import Email, Attachment
from inboxen.helper.user import user_profile

def get_email(user, email_id, preference=None):
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

    plain_attachments = email.attachments.filter(content_type="text/plain")
    html_attachments = email.attachments.filter(content_type="text/html")
    
    if email.body and html_preference < 2:
        # I think we can give them this?
        # I hope noone sets HTML in the email.body
        message["body"] = email.body
        message["attachments"] = email.attachments.all()
     
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
