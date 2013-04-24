import hashlib, time
from datetime import datetime

from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from inboxen.models import Domain, Alias, Tag

@login_required
def add_alias(request):
    
    if request.method == "POST":
        alias = request.POST["alias"]
        domain = Domain.objects.get(domain=request.POST["domain"])
        tags = request.POST["tag"].split(",")
        
        try:
            alias_test = Alias.objects.get(alias=alias, domain=domain)
            return HttpResponseRedirect("/profile")
        except:
            pass 

        new_alias = Alias(alias=alias, domain=domain, user=request.user, created=datetime.now())
        new_alias.save()
        
        for i, tag in enumerate(tags):
            tags[i] = Tag(tag=tag)
            tags[i].alias = new_alias
            tags[i].save()
 
        return HttpResponseRedirect("/profile")

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
        return HttpResponseRedirect("/profile")
    
    context = {
        "page":"Delete Alias",
        "alias":email
    }

    return render(request, "confirm.html", context)
