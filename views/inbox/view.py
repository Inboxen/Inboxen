##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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

from django.utils.translation import ugettext as _
from lxml.html.clean import Cleaner

from django.views import generic

from inboxen import models
from website.views import base

class EmailView(
                base.CommonContextMixin,
                base.LoginRequiredMixin,
                generic.DetailView,
                generic.edit.DeletionMixin
                ):
    model = models.Email
    pk_url_kwarg = "id"

    def get_object(self, *args, **kwargs):
        # Convert the id from base 16 to 10
        self.kwargs[self.pk_url_kwarg] = int(self.kwargs[self.pk_url_kwarg], 16)
        return super(EmailView, self).get_object(*args, **kwargs)

    def get_success_url(self):
        return "/inbox/{0}@{1}/".format(self.kwargs["inbox"], self.kwargs["domain"])

    def get_queryset(self, *args, **kwargs):
        queryset = super(EmailView, self).get_queryset(*args, **kwargs)
        queryset = queryset.filter(
                                    inbox__user=self.request.user,
                                    inbox__inbox=self.kwargs["inbox"],
                                    inbox__domain__domain=self.kwargs["domain"]
                                    ).select_related("inbox", "inbox__domain")
        return queryset

    def find_body(self, html, plain):
        """Given a pair of plaintext and html MIME parts, return True or False
        based on whether the body should be plaintext or not. Returns None
        if there is no viable body
        """
        # find if one is None
        if html is None and plain is None:
            return None
        elif html is None:
            return True
        else: # plain is None
            return False

        # parts are siblings, user preference
        if html.parent == plain.parent:
            pref = self.request.user.userprofile.html_preference
            if pref == 1:
                return True
            elif pref == 2:
                return False
        # which ever has the lower lft value will win
        elif  html.lft < plain.lft:
            return False
        else: # html.lft > plain.lft
            return True

    def get_context_data(self, **kwargs):

        ## the following probably shouldn't be here?

        headers = models.Header.objects.filter(part__email=self.object, part__parent=None)
        headers = headers.get_many("Subject", "From")

        email_dict = {}
        email_dict["subject"] = headers["Subject"]
        email_dict["from"] = headers["From"]
        email_dict["date"] = self.object.received_date
        email_dict["inbox"] = self.object.inbox

        html = None
        plain = None
        attachments = []
        for part in self.object.parts.select_related("body"):
            part_head = part.header_set.get_many("Content-Type", "Content-Disposition")
            part_head["content_type"] = part_head.pop("Content-Type").split(";")
            part_head["content_disposition"] = part_head.pop("Content-Disposition").split(";")
            item = (part, part_head)

            if html is None and part_head["content_type"][0] == "text/html":
                html = item
            elif plain is None and part_head["content_type"][0] == "text/plain":
                plain = item

            attachments.append(item)

        plain_message = self.find_body(html, plain)

        if plain_message is None:
            email_dict["body"] = ""
            plain_message = False
        elif plain_message:
            email_dict["body"] = plain[0].body.data
        else:
            email_dict["body"] = html[0].body.data

        # if siblings, use html_preference
        if not plain_message:
            # Mail Pile uses this, give back if you come up with something better
            cleaner = Cleaner(page_structure=True, meta=True, links=True,
                       javascript=True, scripts=True, frames=True,
                       embedded=True, safe_attrs_only=True)
            email_dict["body"] = cleaner.clean_html(str(email_dict["body"]))

        self.title = email_dict["subject"]

        context = super(EmailView, self).get_context_data(**kwargs)
        context.update({
                        "email": email_dict,
                        "plain_message": plain_message,
                        "attachments": attachments,
                        })

        return context
