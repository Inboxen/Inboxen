
from django.shortcuts import render
from django.http import HttpResponseRedirect
from inboxen.tasks import liberate as data_liberate

def liberate(request):
    if request.method == "POST":
        data_liberate.delay(request.user)
        return HttpResponseRedirect("/user/settings/liberate/done")    

    context = {
        "page":"Liberate your data",
    }
    
    return render(request, "user/settings/liberate/liberate.html", context)
