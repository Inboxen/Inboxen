from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from django.contrib.auth.models import Group
from inboxen.models import Alias, UserProfile, Tag
from inboxen.helper.user import user_profile

@login_required
def settings(request):
    error = ""
    
    # check their html preferences
    profile = user_profile(request.user)
    
    # they submitting it?
    if request.method == "POST":
        try:
            spamfiltering = request.POST["spam_filtering"]
        except:
            spamfiltering = False

        sfg = Group.objects.get(name="SpamFiltering") # spam filtering group

        if spamfiltering and not request.user.groups.filter(name="SpamFiltering").exists():
            request.user.groups.add(sfg)
        elif not spamfiltering and request.user.groups.filter(name="SpamFiltering").exists():
            request.user.groups.remove(sfg)

        request.user.save()

        # Check if they wanted to change the password
        if "password1" in request.POST and "password2" in request.POST and request.POST["password1"]:
            if request.POST["password1"] == request.POST["password2"]:
                request.user.set_password(request.POST["password1"])
                request.user.save()
            else:
                # oh dear lets quickly say no
                error = "Passwords don't match"
        
        profile.html_preference = int(request.POST["html-preference"])
        profile.save()        
        
        if not error:
            # now redirect back to their profile
            return HttpResponseRedirect("/profile")


    # okay they're viewing the settings page
    # we need to load their settings first.
    if request.user.groups.filter(name="SpamFiltering").exists():
        sf = True
    else:
        sf = False

    context = {
        "page":"Settings",
        "spamfiltering":sf,
        "error":error,
        "htmlpreference":int(profile.html_preference),
    }

    return render(request, "settings.html", context)
    
@login_required
def profile(request):

    try:
        aliases = Alias.objects.filter(user=request.user).order_by('-created')
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
    

