##
#    Copyright (C) 2017 Jessica Tallon & Matthew Molyneaux
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.db.models import Case, When, Value, IntegerField

from inboxen.models import Domain, Request
from inboxen.forms.admin import CreateDomainForm, EditDomainForm, EditRequestForm


def domain_admin_index(request):
    domains = Domain.objects.all()

    return TemplateResponse(
        request,
        "inboxen/admin/domain_index.html",
        {"domains": domains},
    )


def domain_admin_create(request):
    if request.method == "POST":
        form = CreateDomainForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("admin:domains:index"))
    else:
        form = CreateDomainForm()

    return TemplateResponse(
        request,
        "inboxen/admin/domain_create.html",
        {"form": form},
    )


def domain_admin_edit(request, domain_pk):
    try:
        domain = Domain.objects.get(pk=domain_pk)
    except Domain.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = EditDomainForm(data=request.POST, instance=domain)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("admin:domains:index"))
    else:
        form = EditDomainForm(instance=domain)

    return TemplateResponse(
        request,
        "inboxen/admin/domain_edit.html",
        {"form": form},
    )


def request_admin_index(request):
    requests = Request.objects.all().annotate(decided=Case(
            When(succeeded__isnull=True, then=Value(1)),
            default_value=Value(0),
            output_field=IntegerField()
        )).\
        order_by("decided", "date").\
        select_related("requester")

    return TemplateResponse(
        request,
        "inboxen/admin/request_index.html",
        {"requests": requests},
    )


def request_admin_edit(request, request_pk):
    try:
        request_obj = Request.objects.get(pk=request_pk)
    except Request.DoesNotExist:
        raise Http404

    previous = Request.objects.\
        filter(requester_id=request_obj.requester_id, succeeded__isnull=False).\
        order_by("date").first()

    if request.method == "POST" and request_obj.succeeded is None:
        form = EditRequestForm(data=request.POST, instance=request_obj, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("admin:requests:index"))
    else:
        form = EditRequestForm(instance=request_obj, user=request.user)

    context = {
        "form": form,
        "req": request_obj,
        "previous": previous,
    }

    return TemplateResponse(
        request,
        "inboxen/admin/request_edit.html",
        context,
    )
