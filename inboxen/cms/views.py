##
#    Copyright (C) 2017 Jessica Tallon & Matt Molyneaux
#
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse

from inboxen.cms.models import HelpBasePage
from inboxen.cms.utils import get_root_page, breadcrumb_iterator
from inboxen.cms.forms import PAGE_TYPES, get_page_form, DeleteForm
from inboxen.cms.decorators import is_secure_admin


def page(request, path):
    path_components = [component for component in path.split('/') if component]
    root_page = get_root_page()
    if root_page is None:
        raise Http404

    page, args, kwargs = root_page.specific.route(request, path_components)

    return page.serve(request, *args, **kwargs)


@is_secure_admin
def index(request, page_pk=None):
    page_qs = HelpBasePage.objects.filter(tree_id=1)

    # either of these should result in a QuerySet with one result
    if page_pk is not None:
        page_qs = page_qs.filter(pk=page_pk)
    else:
        page_qs = page_qs.filter(parent__isnull=True)

    try:
        page = page_qs.get()
    except HelpBasePage.DoesNotExist:
        raise Http404

    context = {
        "page": page,
        "breadcrumbs": breadcrumb_iterator(page),
    }

    return TemplateResponse(
            request,
            "cms/admin/index.html",
            context,
    )


@is_secure_admin
def choose_page_type(request, parent_pk):
    try:
        page = HelpBasePage.objects.get(pk=parent_pk)
    except HelpBasePage.DoesNotExist:
        raise Http404

    context = {
        "models": [model._meta for model in PAGE_TYPES],
        "parent_pk": parent_pk,
        "breadcrumbs": breadcrumb_iterator(page),
    }

    return TemplateResponse(
            request,
            "cms/admin/choose_page_type.html",
            context,
    )


@is_secure_admin
def create_page(request, model, parent_pk):
    try:
        page = HelpBasePage.objects.get(pk=parent_pk)
    except HelpBasePage.DoesNotExist:
        raise Http404

    try:
        model_ct = ContentType.objects.get_by_natural_key(app_label="cms", model=model)
    except ContentType.DoesNotExist:
        raise Http404

    form_class = get_page_form(model_ct)

    if request.method == "POST":
        form = form_class(data=request.POST, files=request.FILES)
        form.instance.parent_id = parent_pk
        form.instance.content_type = model_ct
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("admin:index", kwargs={"page_pk": parent_pk}))
    else:
        form = form_class()

    return TemplateResponse(
            request,
            "cms/admin/create_page.html",
            {
                "form": form,
                "breadcrumbs": breadcrumb_iterator(page),
            }
    )


@is_secure_admin
def edit_page(request, page_pk):
    try:
        page = HelpBasePage.objects.get(pk=page_pk).specific
    except HelpBasePage.DoesNotExist:
        raise Http404

    model_ct = ContentType.objects.get_for_id(page.content_type_id)
    form_class = get_page_form(model_ct)

    if request.method == "POST":
        form = form_class(data=request.POST, files=request.FILES, instance=page)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("admin:index", kwargs={"page_pk": page.pk}))
    else:
        form = form_class(instance=page)

    return TemplateResponse(
            request,
            "cms/admin/edit_page.html",
            {
                "form": form,
                "page": page,
                "breadcrumbs": breadcrumb_iterator(page),
            }
    )


@is_secure_admin
@transaction.atomic
def delete_page(request, page_pk):
    qs = HelpBasePage.objects.filter(lft=(F("rght") - 1))

    try:
        # lft - rght should be 1 if this is a leaf node
        page = qs.get(pk=page_pk).specific
    except HelpBasePage.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = DeleteForm(data=request.POST)
        if form.is_valid():
            kwargs = {}
            if page.parent_id:
                kwargs = {"page_pk": page.parent_id}

            page.delete()
            return HttpResponseRedirect(reverse("admin:index", kwargs=kwargs))
    else:
        form = DeleteForm()

    return TemplateResponse(
            request,
            "cms/admin/delete_page.html",
            {
                "form": form,
                "page": page,
                "breadcrumbs": breadcrumb_iterator(page),
            }
    )
