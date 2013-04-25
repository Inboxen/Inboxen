from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseRedirect

from inboxen.models import Alias, Email, Attachment
from inboxen.helper.email import email 

@login_required
def download_attachment(request, attachment_id):
    try:
        attachment = Attachment.objects.get(id=attachment_id)
    except Exception:
        return HttpResponseRedirect("/")

    response = HttpResponse(attachment.data, content_type=attachment.content_type)
    response["Content-Disposition"] = "attachment; filename=bluhbluh-%s" % attachment_id

    return response

@login_required
def inbox(request, email_address=""):

    error = ""

    if not email_address:
        # assuming global unified inbox
        emails = Email.objects.filter(user=request.user).order_by('-recieved_date')

    else:
        # a specific alias
        alias, domain = email_address.split("@", 1)
        try:
            alias = Alias.objects.get(user=request.user, alias=alias, domain__domain=domain)
            emails = Email.objects.filter(user=request.user, inbox=alias).order_by('-recieved_date') 
        except:
            error = "Can't find email address"

    # lets add the important headers (subject and who sent it (a.k.a. sender))
    for email in emails:
        email.sender, email.subject = "", "(No Subject)"
        for header in email.headers.all():
            if header.name == "From":
                email.sender = header.data
            elif header.name == "Subject":
                email.subject = header.data

    context = {
        "page":"%s - Inbox" % email_address,
        "error":error,
        "emails":emails,
        "email_address":email_address,
    }
    
    return render(request, "inbox.html", context)
    
@login_required
def read_email(request, email_address, emailid):

    alias, domain = email_address.split("@", 1)
    
    try:
        alias = Alias.objects.get(alias=alias, domain__domain=domain, user=request.user)
    except:
        return error_out(page="Inbox", message="Alias doesn't exist")

    try:
        email = email(request.user, emailid)
    except:
        return

    email.subject = "(No subject)"

    # okay we've got the alias and email.
    # now lets get the subject 'n shit
    for header in email.headers.all():
        if header.name == "Subject":
            email.subject = header.data
        elif header.name == "From":
            email.sender = header.data 
     

    context = {
        "page":email.subject,
        "body":email[0],
        "attachments":email[1],
    }
 
    return render(request, "email.html", context)
