##
#    Copyright (C) 2020 Jessica Tallon & Matt Molyneaux
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

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import is_safe_url

from inboxen.models import Email


@login_required
def returned_user(request):
    # this might not be quite right (maybe the user never had any emails)
    emails_deleted = not Email.objects.viewable(request.user.pk).exists()
    request.user.inboxenprofile.receiving_emails = True
    request.user.inboxenprofile.save()
    request.session[settings.USER_SUSPENDED_SESSION_KEY] = False
    context = {"emails_deleted": emails_deleted}
    redirect_to = request.GET.get("next")
    if is_safe_url(redirect_to, allowed_hosts=[request.get_host()], require_https=request.is_secure()):
        context["next"] = redirect_to
    else:
        context["next"] = reverse("user-home")
    return TemplateResponse(request, "account/returned_user.html", context)
