from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inboxen.models import Email, Alias


@login_required
@staff_member_required
def support(request, page=1):
    alias = Alias.objects.filter(alias="support")
    emails = Email.objects.filter(inbox=alias).order_by('-recieved_date')
    
    paginator = Paginator(emails, 100)
    try:
        emails = paginator.page(page)
    except PageNotAnInteger:
        emails = paginator.page(1)
    except EmptyPage:
        emails = paginator.page(paginator.num_pages)

    for email in emails.object_list:
        email.sender, email.subject = "", "(No Subject)"
        for header in email.headers.all():
            if header.name == "From":
                email.sender = header.data
            elif header.name == "Subject":
                email.subject = header.data

    context = {
        "page":"Support Inbox",
        "emails":emails,
    }

    return render(request, "admin/support.html", context)
