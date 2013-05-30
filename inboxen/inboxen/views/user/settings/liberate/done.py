from django.shortcuts import render

def done(request):
    context = {
        "page":"Liberate your data",
    }

    return render(request, "user/settings/liberate/done.html", context)
