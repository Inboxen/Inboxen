from inboxen.models import Email, Attachment
from inboxen.helper.user import user_profile

def email(user, email_id, preference=None):
    """ Gets an email based on user preferences and id of the email """
    # does the user want HTML emails?
    # 0 - don't ever give HTML
    # 1 - prefer plain text but if not HTML
    # 2 - prefer HTML
    if None == preference:
        html_preference = user_profile(user).html_preference
    else:
        html_preference = int(preference)
        
    attachments = email.attachments.all()
    email = Email.objects.get(id=email_id)
    
    if email.body and html_preference < 2:
        # I think we can give them this?
        # I hope noone sets HTML in the email.body
        return email.body
    
    # okay more complicated.
    html_attachment = -1
    plain_attachment = -1
    
    # want plain text if we can
    for aid, attachment in enumerate(attachments):
        if plain_attachment == -1 and attachment.content_type == "text/plain":
            plain_attachment = aid
        if html_attachment == -1 and attachment.content_type == "text/html":
            html_attachments = aid
    
    if preference < 2 and plain_attachment != -1:
        return (attachments.pop(plain_attachment), attachments)
    
    if preference == 0 and html_attachment != -1:
        # we have an html but we don't wanna see html
        # we'll strip the tags out...
        return ("", attachments)
    
    if html_preference != -1:
        return (attachments.pop(html_attachment), attachments)
    
       
       
