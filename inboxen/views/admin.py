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

from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse

from inboxen.cms.decorators import is_secure_admin
from inboxen.models import Domain
from inboxen.forms.admin import CreateDomainForm, EditDomainForm


@is_secure_admin
def domain_admin_index(request):
    domains = Domain.objects.all()

    return TemplateResponse(
        request,
        "inboxen/admin/domain_index.html",
        {"domains": domains},
    )


@is_secure_admin
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


@is_secure_admin
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
