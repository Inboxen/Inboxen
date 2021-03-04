##
#    Copyright (C) 2013, 2019 Jessica Tallon & Matthew Molyneaux
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

from urllib.parse import quote_plus
import re
import unicodedata

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.views import generic

from inboxen import models
from inboxen.liberation.utils import make_message
from inboxen.utils.ratelimit import single_email_ratelimit

HEADER_CLEAN = re.compile(r'\s+')


class AttachmentDownloadView(LoginRequiredMixin, generic.detail.BaseDetailView):
    def get_object(self):
        qs = models.PartList.objects.select_related('body')
        qs = qs.filter(email__deleted=False, email__inbox__user=self.request.user)

        try:
            return qs.get(id=self.kwargs["attachmentid"])
        except models.PartList.DoesNotExist:
            raise Http404

    def render_to_response(self, context):
        # build the Content-Disposition header
        disposition = ["attachment"]

        if self.object.filename:
            # taken django-sendfile2
            # 0d92874bf43966d8e4836c2aba25009d8c1523ac
            # django_sendfile/utils.py, lines 109 to 116
            attachment_filename = self.object.filename
            ascii_filename = unicodedata.normalize('NFKD', attachment_filename)
            ascii_filename = ascii_filename.encode('ascii', 'ignore').decode()
            disposition.append('filename="%s"' % ascii_filename)

            if ascii_filename != attachment_filename:
                quoted_filename = quote_plus(attachment_filename)
                disposition.append('filename*=UTF-8\'\'%s' % quoted_filename)

        disposition = "; ".join(disposition)
        disposition = HEADER_CLEAN.sub(" ", disposition)

        if self.object.content_type:
            content_type = "{0}; charset={1}".format(
                self.object.content_type,
                self.object.charset,
            )
        else:
            content_type = "application/octet-stream"

        # make header object
        data = bytes(self.object.body.data)
        response = HttpResponse(
            content=data,
            status=200,
        )

        response["Content-Length"] = len(data)
        response["Content-Disposition"] = disposition
        response["Content-Type"] = HEADER_CLEAN.sub(" ", content_type)

        return response


@login_required
def download_email(request, inbox=None, domain=None, email=None):
    if single_email_ratelimit.counter_full(request):
        raise Http404

    try:
        email = models.Email.objects.viewable(request.user).filter(
            inbox__inbox=inbox,
            inbox__domain__domain=domain,
        ).select_related("inbox", "inbox__domain").get(id=int(email, 16))
    except models.Email.DoesNotExist:
        raise Http404

    single_email_ratelimit.counter_increase(request)

    msg = make_message(email)
    # set unixfrom to True to turn a single message into a valid mbox
    data = msg.as_bytes(unixfrom=True)

    response = HttpResponse(
        content=data,
        status=200,
    )

    response["Content-Length"] = len(data)
    response["Content-Disposition"] = "attachment; filename={}-{}.mbox".format(str(email.inbox), email)
    response["Content-Type"] = "application/mbox"  # a single email is the same as a mbox

    return response
