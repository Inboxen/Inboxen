import hashlib, time, random

from datetime import datetime

from django.shortcuts import render
from django.http import Http404
from django.contrib.auth import logout
from django.template import RequestContext
from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from inboxen.models import Tag, Domain, Alias, Email

## not for direct display
def error_out(request=None, template="error.html", page="Error", message="There has been a server error"):
    """ Produces an error response """

    context = {
        "page":page,
        "error":message,
    }

    return render(request, template, context)


def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/profile")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect('/profile')
    else:
        form = UserCreationForm()
    
    context = {
        "form":form,
        "page":"Register",
    }

    return render(request, "register.html", context, context_instance=RequestContext(request))

@login_required
def add_alias(request):
    
    if request.method == "POST":
        alias = request.POST["alias"]
        domain = Domain.objects.get(domain=request.POST["domain"])
        tags = request.POST["tag"].split(",")
        
        try:
            alias_test = Alias.objects.get(alias=alias, domain=domain)
            return HttpResponseRedirect("/accounts/profile")
        except:
            pass 

        new_alias = Alias(alias=alias, domain=domain, user=request.user, created=datetime.now())
        new_alias.save()
        
        for i, tag in enumerate(tags):
            tags[i] = Tag(tag=tag)
            tags[i].alias = new_alias
            tags[i].save()
 
        return HttpResponseRedirect("/accounts/profile")

    alias = "%s-%s" % (time.time(), request.user.username) 
    domains = Domain.objects.all()
    
    alias = ""
    count = 0
    while not alias and count < 10:
        alias = "%s-%s" % (time.time(), request.user.username)
        alias = hashlib.sha1(alias).hexdigest()[:count+5]
        try:
            Alias.objects.get(alias=alias)
            alias = ""
            count += 1
        except:
            pass
    context = {
        "page":"Add Alias",
        "domains":domains,
        "alias":alias,
    }
    
    return render(request, "add_alias.html", context)

@login_required
def settings(request):
   
    context = {
        "page":"Settings",
    }

    return render(request, "settings.html", context)

@login_required
def logout_user(request):
    
    logout(request)
    return HttpResponseRedirect("/")

@login_required
def inbox(request, email_address=""):

    error = ""

    if not email_address:
        # assuming global unified inbox
        emails = Email.objects.filter(user=request.user).order_by('recieved_date')

    else:
        # a specific alias
        alias, domain = email_address.split("@", 1)
        try:
            alias = Alias.objects.get(user=request.user, alias=alias, domain__domain=domain)
            emails = Email.objects.filter(user=request.user, inbox=alias).order_by('recieved_date') 
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
        email = Email.objects.get(id=emailid)
    except:
        return error_out(page="Inbox", message="Can't find email")

    email.subject = "(No subject)"

    # okay we've got the alias and email.
    # now lets get the subject 'n shit
    for header in email.headers.all():
        if header.name == "Subject":
            email.subject = header.data
        elif header.name == "From":
            email.sender = header.data 
     

    context = {
        "page":"",
        "email":email,
    }
 
    return render(request, "email.html", context)

@login_required
def profile(request):

    try:
        aliases = Alias.objects.filter(user=request.user).order_by('created')
    except:
        raise
        aliases = []

    try:
        for alias in aliases:
            tag = Tag.objects.filter(alias=alias)
            alias.tags = ", ".join([t.tag for t in tag])
    except:
        pass

    context = {
        "page":"Profile",
        "aliases":aliases,
    }
    
    return render(request, "profile.html", context)

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/profile")

    context = {
        "page":"Login",
    } 

    return render(request, "login.html", context)

@login_required
def delete_alias(request, email):
    if request.method == "POST":
        if request.POST["confirm"] != email:
            raise Http404
        else:
            try:
                email = email.split("@")
                domain = Domain.objects.get(domain=email[1])
                alias = Alias.objects.filter(alias=email[0], domain=domain)
                for a in alias:
                    if a.user == request.user:
                        a.delete()
            except:
                raise Http404
        return HttpResponseRedirect("/accounts/profile")
    
    context = {
        "page":"Delete Alias",
        "alias":email
    }

    return render(request, "confirm.html", context)


def contact(request):
    context ={
        "page":"Contact",
    }

    return render(request, "contact.html", context)

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/accounts/profile")

    context = {
        "page":"Home",
    }

    return render(request, "index.html", context)
